#!/usr/bin/env python
"""html2text: Turn HTML into equivalent Markdown-structured text."""
__version__ = "3.200.3"
__author__ = "Aaron Swartz (me@aaronsw.com)"
__copyright__ = "(C) 2004-2008 Aaron Swartz. GNU GPL 3."
__contributors__ = ["Martin 'Joey' Schulze", "Ricardo Reyes", "Kevin Jay North"]

# TODO:
#   Support decoded entities with unifiable.

try:
    True
except NameError:
    setattr(__builtins__, 'True', 1)
    setattr(__builtins__, 'False', 0)

def has_key(x, y):
    if hasattr(x, 'has_key'): return x.has_key(y)
    else: return y in x

import numpy as np
import time
import random
import sys
import json
import string
import urllib2
keep = string.lowercase + string.digits + string.whitespace
table = string.maketrans(keep, keep)
delete = ''.join(set(string.printable) - set(keep))
from nltk.corpus import wordnet
from pattern.en import singularize, pluralize
from pint import UnitRegistry
ureg = UnitRegistry()
import sqlite3 as lite

try:
    import htmlentitydefs
    import urlparse
    import HTMLParser
except ImportError: #Python3
    import html.entities as htmlentitydefs
    import urllib.parse as urlparse
    import html.parser as HTMLParser
try: #Python3
    import urllib.request as urllib
except:
    import urllib
import optparse, re, sys, codecs, types

try: from textwrap import wrap
except: pass

con = lite.connect('db')

# Use Unicode characters instead of their ascii psuedo-replacements
UNICODE_SNOB = 0

# Escape all special characters.  Output is less readable, but avoids corner case formatting issues.
ESCAPE_SNOB = 0

# Put the links after each paragraph instead of at the end.
LINKS_EACH_PARAGRAPH = 0

# Wrap long lines at position. 0 for no wrapping. (Requires Python 2.3.)
BODY_WIDTH = 78

# Don't show internal links (href="#local-anchor") -- corresponding link targets
# won't be visible in the plain text file anyway.
SKIP_INTERNAL_LINKS = True

# Use inline, rather than reference, formatting for images and links
INLINE_LINKS = True

# Number of pixels Google indents nested lists
GOOGLE_LIST_INDENT = 36

IGNORE_ANCHORS = True
IGNORE_IMAGES = True
IGNORE_EMPHASIS = True

### Entity Nonsense ###

def name2cp(k):
    if k == 'apos': return ord("'")
    if hasattr(htmlentitydefs, "name2codepoint"): # requires Python 2.3
        return htmlentitydefs.name2codepoint[k]
    else:
        k = htmlentitydefs.entitydefs[k]
        if k.startswith("&#") and k.endswith(";"): return int(k[2:-1]) # not in latin-1
        return ord(codecs.latin_1_decode(k)[0])

unifiable = {'rsquo':"'", 'lsquo':"'", 'rdquo':'"', 'ldquo':'"',
'copy':'(C)', 'mdash':'--', 'nbsp':' ', 'rarr':'->', 'larr':'<-', 'middot':'*',
'ndash':'-', 'oelig':'oe', 'aelig':'ae',
'agrave':'a', 'aacute':'a', 'acirc':'a', 'atilde':'a', 'auml':'a', 'aring':'a',
'egrave':'e', 'eacute':'e', 'ecirc':'e', 'euml':'e',
'igrave':'i', 'iacute':'i', 'icirc':'i', 'iuml':'i',
'ograve':'o', 'oacute':'o', 'ocirc':'o', 'otilde':'o', 'ouml':'o',
'ugrave':'u', 'uacute':'u', 'ucirc':'u', 'uuml':'u',
'lrm':'', 'rlm':''}

unifiable_n = {}

for k in unifiable.keys():
    unifiable_n[name2cp(k)] = unifiable[k]

### End Entity Nonsense ###

def onlywhite(line):
    """Return true if the line does only consist of whitespace characters."""
    for c in line:
        if c is not ' ' and c is not '  ':
            return c is ' '
    return line

def hn(tag):
    if tag[0] == 'h' and len(tag) == 2:
        try:
            n = int(tag[1])
            if n in range(1, 10): return n
        except ValueError: return 0

def dumb_property_dict(style):
    """returns a hash of css attributes"""
    return dict([(x.strip(), y.strip()) for x, y in [z.split(':', 1) for z in style.split(';') if ':' in z]]);

def dumb_css_parser(data):
    """returns a hash of css selectors, each of which contains a hash of css attributes"""
    # remove @import sentences
    data += ';'
    importIndex = data.find('@import')
    while importIndex != -1:
        data = data[0:importIndex] + data[data.find(';', importIndex) + 1:]
        importIndex = data.find('@import')

    # parse the css. reverted from dictionary compehension in order to support older pythons
    elements =  [x.split('{') for x in data.split('}') if '{' in x.strip()]
    try:
        elements = dict([(a.strip(), dumb_property_dict(b)) for a, b in elements])
    except ValueError:
        elements = {} # not that important

    return elements

def element_style(attrs, style_def, parent_style):
    """returns a hash of the 'final' style attributes of the element"""
    style = parent_style.copy()
    if 'class' in attrs:
        for css_class in attrs['class'].split():
            css_style = style_def['.' + css_class]
            style.update(css_style)
    if 'style' in attrs:
        immediate_style = dumb_property_dict(attrs['style'])
        style.update(immediate_style)
    return style

def google_list_style(style):
    """finds out whether this is an ordered or unordered list"""
    if 'list-style-type' in style:
        list_style = style['list-style-type']
        if list_style in ['disc', 'circle', 'square', 'none']:
            return 'ul'
    return 'ol'

def google_has_height(style):
    """check if the style of the element has the 'height' attribute explicitly defined"""
    if 'height' in style:
        return True
    return False

def google_text_emphasis(style):
    """return a list of all emphasis modifiers of the element"""
    emphasis = []
    if 'text-decoration' in style:
        emphasis.append(style['text-decoration'])
    if 'font-style' in style:
        emphasis.append(style['font-style'])
    if 'font-weight' in style:
        emphasis.append(style['font-weight'])
    return emphasis

def google_fixed_width_font(style):
    """check if the css of the current element defines a fixed width font"""
    font_family = ''
    if 'font-family' in style:
        font_family = style['font-family']
    if 'Courier New' == font_family or 'Consolas' == font_family:
        return True
    return False

def list_numbering_start(attrs):
    """extract numbering from list element attributes"""
    if 'start' in attrs:
        return int(attrs['start']) - 1
    else:
        return 0

class HTML2Text(HTMLParser.HTMLParser):
    def __init__(self, out=None, baseurl=''):
        HTMLParser.HTMLParser.__init__(self)

        # Config options
        self.unicode_snob = UNICODE_SNOB
        self.escape_snob = ESCAPE_SNOB
        self.links_each_paragraph = LINKS_EACH_PARAGRAPH
        self.body_width = BODY_WIDTH
        self.skip_internal_links = SKIP_INTERNAL_LINKS
        self.inline_links = INLINE_LINKS
        self.google_list_indent = GOOGLE_LIST_INDENT
        self.ignore_links = IGNORE_ANCHORS
        self.ignore_images = IGNORE_IMAGES
        self.ignore_emphasis = IGNORE_EMPHASIS
        self.google_doc = False
        self.ul_item_mark = '*'
        self.emphasis_mark = '_'
        self.strong_mark = '**'

        if out is None:
            self.out = self.outtextf
        else:
            self.out = out

        self.outtextlist = []  # empty list to store output characters before they are "joined"

        try:
            self.outtext = unicode()
        except NameError:  # Python3
            self.outtext = str()

        self.quiet = 0
        self.p_p = 0  # number of newline character to print before next output
        self.outcount = 0
        self.start = 1
        self.space = 0
        self.a = []
        self.astack = []
        self.maybe_automatic_link = None
        self.absolute_url_matcher = re.compile(r'^[a-zA-Z+]+://')
        self.acount = 0
        self.list = []
        self.blockquote = 0
        self.pre = 0
        self.startpre = 0
        self.code = False
        self.br_toggle = ''
        self.lastWasNL = 0
        self.lastWasList = False
        self.style = 0
        self.style_def = {}
        self.tag_stack = []
        self.emphasis = 0
        self.drop_white_space = 0
        self.inheader = False
        self.abbr_title = None  # current abbreviation definition
        self.abbr_data = None  # last inner HTML (for abbr being defined)
        self.abbr_list = {}  # stack of abbreviations to write later
        self.baseurl = baseurl

        try: del unifiable_n[name2cp('nbsp')]
        except KeyError: pass
        unifiable['nbsp'] = '&nbsp_place_holder;'


    def feed(self, data):
        data = data.replace("</' + 'script>", "</ignore>")
        HTMLParser.HTMLParser.feed(self, data)

    def handle(self, data):
        self.feed(data)
        self.feed("")
        return self.optwrap(self.close())

    def outtextf(self, s):
        self.outtextlist.append(s)
        if s: self.lastWasNL = s[-1] == '\n'

    def close(self):
        HTMLParser.HTMLParser.close(self)

        self.pbr()
        self.o('', 0, 'end')

        self.outtext = self.outtext.join(self.outtextlist)
        if self.unicode_snob:
            nbsp = unichr(name2cp('nbsp'))
        else:
            nbsp = u' '
        self.outtext = self.outtext.replace(u'&nbsp_place_holder;', nbsp)

        return self.outtext

    def handle_charref(self, c):
        self.o(self.charref(c), 1)

    def handle_entityref(self, c):
        self.o(self.entityref(c), 1)

    def handle_starttag(self, tag, attrs):
        self.handle_tag(tag, attrs, 1)

    def handle_endtag(self, tag):
        self.handle_tag(tag, None, 0)

    def previousIndex(self, attrs):
        """ returns the index of certain set of attributes (of a link) in the
            self.a list

            If the set of attributes is not found, returns None
        """
        if not has_key(attrs, 'href'): return None

        i = -1
        for a in self.a:
            i += 1
            match = 0

            if has_key(a, 'href') and a['href'] == attrs['href']:
                if has_key(a, 'title') or has_key(attrs, 'title'):
                        if (has_key(a, 'title') and has_key(attrs, 'title') and
                            a['title'] == attrs['title']):
                            match = True
                else:
                    match = True

            if match: return i

    def drop_last(self, nLetters):
        if not self.quiet:
            self.outtext = self.outtext[:-nLetters]

    def handle_emphasis(self, start, tag_style, parent_style):
        """handles various text emphases"""
        tag_emphasis = google_text_emphasis(tag_style)
        parent_emphasis = google_text_emphasis(parent_style)

        # handle Google's text emphasis
        strikethrough =  'line-through' in tag_emphasis and self.hide_strikethrough
        bold = 'bold' in tag_emphasis and not 'bold' in parent_emphasis
        italic = 'italic' in tag_emphasis and not 'italic' in parent_emphasis
        fixed = google_fixed_width_font(tag_style) and not \
                google_fixed_width_font(parent_style) and not self.pre

        if start:
            # crossed-out text must be handled before other attributes
            # in order not to output qualifiers unnecessarily
            if bold or italic or fixed:
                self.emphasis += 1
            if strikethrough:
                self.quiet += 1
            if italic:
                self.o(self.emphasis_mark)
                self.drop_white_space += 1
            if bold:
                self.o(self.strong_mark)
                self.drop_white_space += 1
            if fixed:
                self.o('`')
                self.drop_white_space += 1
                self.code = True
        else:
            if bold or italic or fixed:
                # there must not be whitespace before closing emphasis mark
                self.emphasis -= 1
                self.space = 0
                self.outtext = self.outtext.rstrip()
            if fixed:
                if self.drop_white_space:
                    # empty emphasis, drop it
                    self.drop_last(1)
                    self.drop_white_space -= 1
                else:
                    self.o('`')
                self.code = False
            if bold:
                if self.drop_white_space:
                    # empty emphasis, drop it
                    self.drop_last(2)
                    self.drop_white_space -= 1
                else:
                    self.o(self.strong_mark)
            if italic:
                if self.drop_white_space:
                    # empty emphasis, drop it
                    self.drop_last(1)
                    self.drop_white_space -= 1
                else:
                    self.o(self.emphasis_mark)
            # space is only allowed after *all* emphasis marks
            if (bold or italic) and not self.emphasis:
                    self.o(" ")
            if strikethrough:
                self.quiet -= 1

    def handle_tag(self, tag, attrs, start):
        #attrs = fixattrs(attrs)
        if attrs is None:
            attrs = {}
        else:
            attrs = dict(attrs)

        if self.google_doc:
            # the attrs parameter is empty for a closing tag. in addition, we
            # need the attributes of the parent nodes in order to get a
            # complete style description for the current element. we assume
            # that google docs export well formed html.
            parent_style = {}
            if start:
                if self.tag_stack:
                  parent_style = self.tag_stack[-1][2]
                tag_style = element_style(attrs, self.style_def, parent_style)
                self.tag_stack.append((tag, attrs, tag_style))
            else:
                dummy, attrs, tag_style = self.tag_stack.pop()
                if self.tag_stack:
                    parent_style = self.tag_stack[-1][2]

        if hn(tag):
            self.p()
            if start:
                self.inheader = True
                self.o(hn(tag)*"#" + ' ')
            else:
                self.inheader = False
                return # prevent redundant emphasis marks on headers

        if tag in ['p', 'div']:
            if self.google_doc:
                if start and google_has_height(tag_style):
                    self.p()
                else:
                    self.soft_br()
            else:
                self.p()

        if tag == "br" and start: self.o("  \n")

        if tag == "hr" and start:
            self.p()
            self.o("* * *")
            self.p()

        if tag in ["head", "style", 'script']:
            if start: self.quiet += 1
            else: self.quiet -= 1

        if tag == "style":
            if start: self.style += 1
            else: self.style -= 1

        if tag in ["body"]:
            self.quiet = 0 # sites like 9rules.com never close <head>

        if tag == "blockquote":
            if start:
                self.p(); self.o('> ', 0, 1); self.start = 1
                self.blockquote += 1
            else:
                self.blockquote -= 1
                self.p()

        if tag in ['em', 'i', 'u'] and not self.ignore_emphasis: self.o(self.emphasis_mark)
        if tag in ['strong', 'b'] and not self.ignore_emphasis: self.o(self.strong_mark)
        if tag in ['del', 'strike', 's']:
            if start:
                self.o("<"+tag+">")
            else:
                self.o("</"+tag+">")

        if self.google_doc:
            if not self.inheader:
                # handle some font attributes, but leave headers clean
                self.handle_emphasis(start, tag_style, parent_style)

        if tag in ["code", "tt"] and not self.pre: self.o('`') #TODO: `` `this` ``
        if tag == "abbr":
            if start:
                self.abbr_title = None
                self.abbr_data = ''
                if has_key(attrs, 'title'):
                    self.abbr_title = attrs['title']
            else:
                if self.abbr_title != None:
                    self.abbr_list[self.abbr_data] = self.abbr_title
                    self.abbr_title = None
                self.abbr_data = ''

        if tag == "a" and not self.ignore_links:
            if start:
                if has_key(attrs, 'href') and not (self.skip_internal_links and attrs['href'].startswith('#')):
                    self.astack.append(attrs)
                    self.maybe_automatic_link = attrs['href']
                else:
                    self.astack.append(None)
            else:
                if self.astack:
                    a = self.astack.pop()
                    if self.maybe_automatic_link:
                        self.maybe_automatic_link = None
                    elif a:
                        if self.inline_links:
                            self.o("](" + escape_md(a['href']) + ")")
                        else:
                            i = self.previousIndex(a)
                            if i is not None:
                                a = self.a[i]
                            else:
                                self.acount += 1
                                a['count'] = self.acount
                                a['outcount'] = self.outcount
                                self.a.append(a)
                            self.o("][" + str(a['count']) + "]")

        if tag == "img" and start and not self.ignore_images:
            if has_key(attrs, 'src'):
                attrs['href'] = attrs['src']
                alt = attrs.get('alt', '')
                self.o("![" + escape_md(alt) + "]")

                if self.inline_links:
                    self.o("(" + escape_md(attrs['href']) + ")")
                else:
                    i = self.previousIndex(attrs)
                    if i is not None:
                        attrs = self.a[i]
                    else:
                        self.acount += 1
                        attrs['count'] = self.acount
                        attrs['outcount'] = self.outcount
                        self.a.append(attrs)
                    self.o("[" + str(attrs['count']) + "]")

        if tag == 'dl' and start: self.p()
        if tag == 'dt' and not start: self.pbr()
        if tag == 'dd' and start: self.o('    ')
        if tag == 'dd' and not start: self.pbr()

        if tag in ["ol", "ul"]:
            # Google Docs create sub lists as top level lists
            if (not self.list) and (not self.lastWasList):
                self.p()
            if start:
                if self.google_doc:
                    list_style = google_list_style(tag_style)
                else:
                    list_style = tag
                numbering_start = list_numbering_start(attrs)
                self.list.append({'name':list_style, 'num':numbering_start})
            else:
                if self.list: self.list.pop()
            self.lastWasList = True
        else:
            self.lastWasList = False

        if tag == 'li':
            self.pbr()
            if start:
                if self.list: li = self.list[-1]
                else: li = {'name':'ul', 'num':0}
                if self.google_doc:
                    nest_count = self.google_nest_count(tag_style)
                else:
                    nest_count = len(self.list)
                self.o("  " * nest_count) #TODO: line up <ol><li>s > 9 correctly.
                if li['name'] == "ul": self.o(self.ul_item_mark + " ")
                elif li['name'] == "ol":
                    li['num'] += 1
                    self.o(str(li['num'])+". ")
                self.start = 1

        if tag in ["table", "tr"] and start: self.p()
        if tag == 'td': self.pbr()

        if tag == "pre":
            if start:
                self.startpre = 1
                self.pre = 1
            else:
                self.pre = 0
            self.p()

    def pbr(self):
        if self.p_p == 0:
            self.p_p = 1

    def p(self):
        self.p_p = 2

    def soft_br(self):
        self.pbr()
        self.br_toggle = '  '

    def o(self, data, puredata=0, force=0):
        if self.abbr_data is not None:
            self.abbr_data += data

        if not self.quiet:
            if self.google_doc:
                # prevent white space immediately after 'begin emphasis' marks ('**' and '_')
                lstripped_data = data.lstrip()
                if self.drop_white_space and not (self.pre or self.code):
                    data = lstripped_data
                if lstripped_data != '':
                    self.drop_white_space = 0

            if puredata and not self.pre:
                data = re.sub('\s+', ' ', data)
                if data and data[0] == ' ':
                    self.space = 1
                    data = data[1:]
            if not data and not force: return

            if self.startpre:
                #self.out(" :") #TODO: not output when already one there
                if not data.startswith("\n"):  # <pre>stuff...
                    data = "\n" + data
            bq = (">" * self.blockquote)
            if not (force and data and data[0] == ">") and self.blockquote: bq += " "

            if self.pre:
                if not self.list:
                    bq += "    "
                #else: list content is already partially indented
                for i in xrange(len(self.list)):
                    bq += "    "
                data = data.replace("\n", "\n"+bq)

            if self.startpre:
                self.startpre = 0
                if self.list:
                    data = data.lstrip("\n") # use existing initial indentation

            if self.start:
                self.space = 0
                self.p_p = 0
                self.start = 0

            if force == 'end':
                # It's the end.
                self.p_p = 0
                self.out("\n")
                self.space = 0

            if self.p_p:
                self.out((self.br_toggle+'\n'+bq)*self.p_p)
                self.space = 0
                self.br_toggle = ''

            if self.space:
                if not self.lastWasNL: self.out(' ')
                self.space = 0

            if self.a and ((self.p_p == 2 and self.links_each_paragraph) or force == "end"):
                if force == "end": self.out("\n")

                newa = []
                for link in self.a:
                    if self.outcount > link['outcount']:
                        self.out("   ["+ str(link['count']) +"]: " + urlparse.urljoin(self.baseurl, link['href']))
                        if has_key(link, 'title'): self.out(" ("+link['title']+")")
                        self.out("\n")
                    else:
                        newa.append(link)

                if self.a != newa: self.out("\n") # Don't need an extra line when nothing was done.

                self.a = newa

            if self.abbr_list and force == "end":
                for abbr, definition in self.abbr_list.items():
                    self.out("  *[" + abbr + "]: " + definition + "\n")

            self.p_p = 0
            self.out(data)
            self.outcount += 1

    def handle_data(self, data):
        if r'\/script>' in data: self.quiet -= 1

        if self.style:
            self.style_def.update(dumb_css_parser(data))

        if not self.maybe_automatic_link is None:
            href = self.maybe_automatic_link
            if href == data and self.absolute_url_matcher.match(href):
                self.o("<" + data + ">")
                return
            else:
                self.o("[")
                self.maybe_automatic_link = None

        if not self.code and not self.pre:
            data = escape_md_section(data, snob=self.escape_snob)
        self.o(data, 1)

    def unknown_decl(self, data): pass

    def charref(self, name):
        if name[0] in ['x','X']:
            c = int(name[1:], 16)
        else:
            c = int(name)

        if not self.unicode_snob and c in unifiable_n.keys():
            return unifiable_n[c]
        else:
            try:
                return unichr(c)
            except NameError: #Python3
                return chr(c)

    def entityref(self, c):
        if not self.unicode_snob and c in unifiable.keys():
            return unifiable[c]
        else:
            try: name2cp(c)
            except KeyError: return "&" + c + ';'
            else:
                try:
                    return unichr(name2cp(c))
                except NameError: #Python3
                    return chr(name2cp(c))

    def replaceEntities(self, s):
        s = s.group(1)
        if s[0] == "#":
            return self.charref(s[1:])
        else: return self.entityref(s)

    r_unescape = re.compile(r"&(#?[xX]?(?:[0-9a-fA-F]+|\w{1,8}));")
    def unescape(self, s):
        return self.r_unescape.sub(self.replaceEntities, s)

    def google_nest_count(self, style):
        """calculate the nesting count of google doc lists"""
        nest_count = 0
        if 'margin-left' in style:
            nest_count = int(style['margin-left'][:-2]) / self.google_list_indent
        return nest_count


    def optwrap(self, text):
        """Wrap all paragraphs in the provided text."""
        if not self.body_width:
            return text

        assert wrap, "Requires Python 2.3."
        result = ''
        newlines = 0
        for para in text.split("\n"):
            if len(para) > 0:
                if not skipwrap(para):
                    result += "\n".join(wrap(para, self.body_width))
                    if para.endswith('  '):
                        result += "  \n"
                        newlines = 1
                    else:
                        result += "\n\n"
                        newlines = 2
                else:
                    if not onlywhite(para):
                        result += para + "\n"
                        newlines = 1
            else:
                if newlines < 2:
                    result += "\n"
                    newlines += 1
        return result

ordered_list_matcher = re.compile(r'\d+\.\s')
unordered_list_matcher = re.compile(r'[-\*\+]\s')
md_chars_matcher = re.compile(r"([\\\[\]\(\)])")
md_chars_matcher_all = re.compile(r"([`\*_{}\[\]\(\)#!])")
md_dot_matcher = re.compile(r"""
    ^             # start of line
    (\s*\d+)      # optional whitespace and a number
    (\.)          # dot
    (?=\s)        # lookahead assert whitespace
    """, re.MULTILINE | re.VERBOSE)
md_plus_matcher = re.compile(r"""
    ^
    (\s*)
    (\+)
    (?=\s)
    """, flags=re.MULTILINE | re.VERBOSE)
md_dash_matcher = re.compile(r"""
    ^
    (\s*)
    (-)
    (?=\s|\-)     # followed by whitespace (bullet list, or spaced out hr)
                  # or another dash (header or hr)
    """, flags=re.MULTILINE | re.VERBOSE)
slash_chars = r'\`*_{}[]()#+-.!'
md_backslash_matcher = re.compile(r'''
    (\\)          # match one slash
    (?=[%s])      # followed by a char that requires escaping
    ''' % re.escape(slash_chars),
    flags=re.VERBOSE)

def skipwrap(para):
    # If the text begins with four spaces or one tab, it's a code block; don't wrap
    if para[0:4] == '    ' or para[0] == '\t':
        return True
    # If the text begins with only two "--", possibly preceded by whitespace, that's
    # an emdash; so wrap.
    stripped = para.lstrip()
    if stripped[0:2] == "--" and len(stripped) > 2 and stripped[2] != "-":
        return False
    # I'm not sure what this is for; I thought it was to detect lists, but there's
    # a <br>-inside-<span> case in one of the tests that also depends upon it.
    if stripped[0:1] == '-' or stripped[0:1] == '*':
        return True
    # If the text begins with a single -, *, or +, followed by a space, or an integer,
    # followed by a ., followed by a space (in either case optionally preceeded by
    # whitespace), it's a list; don't wrap.
    if ordered_list_matcher.match(stripped) or unordered_list_matcher.match(stripped):
        return True
    return False

def wrapwrite(text):
    text = text.encode('utf-8')
    try: #Python3
        sys.stdout.buffer.write(text)
    except AttributeError:
        sys.stdout.write(text)

def html2text(html, baseurl=''):
    h = HTML2Text(baseurl=baseurl)
    return h.handle(html)

def unescape(s, unicode_snob=False):
    h = HTML2Text()
    h.unicode_snob = unicode_snob
    return h.unescape(s)

def escape_md(text):
    """Escapes markdown-sensitive characters within other markdown constructs."""
    return md_chars_matcher.sub(r"\\\1", text)

def escape_md_section(text, snob=False):
    """Escapes markdown-sensitive characters across whole document sections."""
    text = md_backslash_matcher.sub(r"\\\1", text)
    if snob:
        text = md_chars_matcher_all.sub(r"\\\1", text)
    text = md_dot_matcher.sub(r"\1\\\2", text)
    text = md_plus_matcher.sub(r"\1\\\2", text)
    text = md_dash_matcher.sub(r"\1\\\2", text)
    return text


def main(html):
    print "downloading html..."
    baseurl = ''

    p = optparse.OptionParser('%prog [(filename|url) [encoding]]',
                              version='%prog ' + __version__)
    p.add_option("--ignore-emphasis", dest="ignore_emphasis", action="store_true",
        default=IGNORE_EMPHASIS, help="don't include any formatting for emphasis")
    p.add_option("--ignore-links", dest="ignore_links", action="store_true",
        default=IGNORE_ANCHORS, help="don't include any formatting for links")
    p.add_option("--ignore-images", dest="ignore_images", action="store_true",
        default=IGNORE_IMAGES, help="don't include any formatting for images")
    p.add_option("-g", "--google-doc", action="store_true", dest="google_doc",
        default=False, help="convert an html-exported Google Document")
    p.add_option("-d", "--dash-unordered-list", action="store_true", dest="ul_style_dash",
        default=True, help="use a dash rather than a star for unordered list items")
    p.add_option("-e", "--asterisk-emphasis", action="store_true", dest="em_style_asterisk",
        default=True, help="use an asterisk rather than an underscore for emphasized text")
    p.add_option("-b", "--body-width", dest="body_width", action="store", type="int",
        default=BODY_WIDTH, help="number of characters per output line, 0 for no wrap")
    p.add_option("-i", "--google-list-indent", dest="list_indent", action="store", type="int",
        default=GOOGLE_LIST_INDENT, help="number of pixels Google indents nested lists")
    p.add_option("-s", "--hide-strikethrough", action="store_true", dest="hide_strikethrough",
        default=True, help="hide strike-through text. only relevant when -g is specified as well")
    p.add_option("--escape-all", action="store_true", dest="escape_snob",
        default=False, help="Escape all special characters.  Output is less readable, but avoids corner case formatting issues.")
    (options, args) = p.parse_args()
    # process input
    encoding = "utf-8"
    if len(args) > -1:
        file_ = html
        if len(args) == 29:
            encoding = args[1]
        if len(args) > 29:
            p.error('Too many arguments')

        if file_.startswith('http://') or file_.startswith('https://'):
            baseurl = file_
            #j = urllib.urlopen(baseurl)
            opener = urllib2.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0')]
            j = opener.open(baseurl)
            data = j.read()
            if encoding is None:
                try:
                    from feedparser import _getCharacterEncoding as enc
                except ImportError:
                    enc = lambda x, y: ('utf-8', 1)
                encoding = enc(j.headers, data)[0]
                if encoding == 'us-ascii':
                    encoding = 'utf-8'
        else:
            data = open(file_, 'rb').read()
            if encoding is None:
                try:
                    from chardet import detect
                except ImportError:
                    detect = lambda x: {'encoding': 'utf-8'}
                encoding = detect(data)['encoding']
    else:
        data = sys.stdin.read()

    data = data.decode(encoding)
    h = HTML2Text(baseurl=baseurl)
    # handle options
    if options.ul_style_dash: h.ul_item_mark = '-'
    if options.em_style_asterisk:
        h.emphasis_mark = '*'
        h.strong_mark = '__'

    h.body_width = options.body_width
    h.list_indent = options.list_indent
    h.ignore_emphasis = options.ignore_emphasis
    h.ignore_links = options.ignore_links
    h.ignore_images = options.ignore_images
    h.google_doc = options.google_doc
    h.hide_strikethrough = options.hide_strikethrough
    h.escape_snob = options.escape_snob

    #wrapwrite(h.handle(data))
    #with open('test','w') as file:
     # file.write(h.handle(data).encode('utf-8'))
    return h.handle(data).encode('utf-8')

def count_occurrences(word, sentence):
    return sentence.lower().translate(table, delete).split().count(word)

def extract_recipe(data):
    print "extracting recipe directions..."
    
    
    recipe_language = ['aioloi', 'aged','adjust','braise','infuse','homogenize','blend','brush','line','lard','carmelize','peel','emulsify','preheat','rack','pan','grease','butter','medium','pan','stir','bowl','set','whisk','egg','mix','cook','saute','minute','heat','batter','oven','hot','bake','cut','tender','grill','cool','serving','cheese','mint','serve','season','salt','drain','dente','firm','lid','prepare','oil','grind','mash','squash','trim','ingredient','baking','foil','silicone','parchment','bag','small','pepper','drizzle','shake','moist','taste','add','sprinkle','spread','dry','place','bread','machine','start','raised','knead','raise','rise','spread','scrub','chunk','toss','chop','aside','brown','quench','reduce','roast','scald','sauce','seer','sift','skim','smoke','temper','zest','slice','flat','broil','fill','olive','tablespoon','oz','hand','water','separate','flour','coat','fridge','golden','fresh','ground','refresh','together','dice','rinse','melt','pour','squeeze','liquid','mince','combine','fluffy','pinch','apart','sheet','transfer','fry','film','cover','leave','juice','job','seed','top','off','on','decorate','mold','rub','crosshatch','knife','sharp','preheat','finely','processor','extract','stiff','nonstick']

    
    line_count = 0
    a=np.array([0])
    dp=np.array([0])
    for line in data.split('\n'):
        a = np.append(a,[0])
        dp = np.append(dp,[0])
        for word in recipe_language:
          a[line_count] = a[line_count] + count_occurrences(word,line.lower())
        if '##' in line:
          dp[line_count]  = 1
        line_count = line_count + 1
    np.set_printoptions(threshold='nan',linewidth=75000)
    #print repr(a)
    #print repr(dp)

    b=np.array([])
    bx=np.array([])
    for i in np.arange(1,len(a)-7,7):
        b = np.append(b,np.sum(a[i:i+7]))
        bx=np.append(bx,i+4)
    #print repr(b)
    maxInd = bx[np.argmax(b)]

    numZero = 0
    for i in np.arange(maxInd,len(a),1):
        if a[i]>0:
            numZero = 0;
        else:
            numZero = numZero + 1
        if numZero > 4:
            break
    endInd = i-4

    numZero = 0
    for i in np.arange(maxInd,1,-1):
        if a[i]>0:
            numZero = 0;
        else:
            numZero = numZero + 1
        if numZero > 4:
            break
    startInd = i+4
    
    numZero = 0
    for i in np.arange(maxInd,1,-1):
        if dp[i]>0:
            break
    startIndDp = i
    
    numZero = 0
    for i in np.arange(maxInd,len(a),1):
        if dp[i]>0:
            break
    endIndDp = i

    if startInd < startIndDp:
        startInd = startIndDp
        
    if endInd > endIndDp:
        endInd = endIndDp-1
    #print startInd
    #print maxInd
    #print endInd
    finalString = ""
    if np.max(b) > 9:
        line_count = 0
        for line in data.split('\n'):
            if line_count >= startInd and line_count <= endInd and '#' not in line and len(line)>3:
                finalString = finalString + line + "\n"
            line_count = line_count + 1
    else:
        return "no recipe found"
    return finalString

    

def extract_ingredients(data):
    print "extracting ingredients..."

    recipe_language = ['cup','can','jar','package','ounce','pound','whole','tablespoon','teaspoon','salt','pinch','/','-','3/4','1/2','1/8','fresh','to taste','chops','container','1/4','3/8','5/8','1/4']
    
    line_count = 0
    a=np.array([0])
    dp=np.array([0])
    for line in data.split('\n'):
        a = np.append(a,[0])
        dp = np.append(dp,[0])
        if len(line) > 15 and len(line)<90:
          for word in recipe_language:
              if word in line.lower():
                  a[line_count] = a[line_count] + 1
        if '##' in line:
          dp[line_count]  = 1
        if '# Ingredients' in line:
          a[line_count+1] = a[line_count+1] + 5
        if line.count('#') == 1:
          title = line
        line_count = line_count + 1
    np.set_printoptions(threshold='nan',linewidth=75000)
    titleString = title
    #print repr(a)
    #print repr(dp)

    b=np.array([])
    bx=np.array([])
    for i in np.arange(1,len(a)-5,5):
        b = np.append(b,np.sum(a[i:i+5]))
        bx=np.append(bx,i+3)
    #print repr(b)
    maxInd = bx[np.argmax(b)]

    numZero = 0
    for i in np.arange(maxInd,len(a),1):
        if a[i]>0:
            numZero = 0;
        else:
            numZero = numZero + 1
        if numZero > 4:
            break
    endInd = i-4

    numZero = 0
    for i in np.arange(maxInd,1,-1):
        if a[i]>0:
            numZero = 0;
        else:
            numZero = numZero + 1
        if numZero > 4:
            break
    startInd = i+4
    
    numZero = 0
    for i in np.arange(maxInd,1,-1):
        if dp[i]>0:
            break
    startIndDp = i
    
    numZero = 0
    for i in np.arange(maxInd,len(a),1):
        if dp[i]>0:
            break
    endIndDp = i

    if startInd < startIndDp:
        startInd = startIndDp
        
    if endInd > endIndDp:
        endInd = endIndDp-1
    #print startInd
    #print maxInd
    #print endInd
    finalString = ""
    if np.max(b) > 4:
        line_count = 0
        for line in data.split('\n'):
            if line_count >= startInd and line_count <= endInd and '#' not in line and len(line)>3:
                finalString = finalString + line + "\n"
            line_count = line_count + 1
    else:
        return "no ingredients found"
    return (titleString,finalString)



def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)
    
def getFoodFromDatabase(sentence,nutrition):
  # Remove things in parentheses
  regEx = re.compile(r'([^\(]*)\([^\)]*\) *(.*)')
  m = regEx.match(sentence)
  while m:
    sentence = m.group(1) + m.group(2)
    m = regEx.match(sentence)
  
  sentence = sentence.lower()
  sentence = sentence.replace('-',' ')
  sentence = sentence.replace(' or ',' ')
  sentence = sentence.replace(' and ',' ')
  sentence = sentence.replace(' to ',' ')
  sentence = sentence.replace(' for ',' ')
  sentence = sentence.replace('(','')
  sentence = sentence.replace(')','')
  sentence = sentence.replace('about','')
  sentence = sentence.replace('and/or','')
  sentence = sentence.replace('/','slashslash')
  

  # Remove puncuation
  exclude = set(string.punctuation)
  sentence = ''.join(ch for ch in sentence if ch not in exclude)
    
  sentence = sentence.replace('slashslash','/')
  print "sentence"+sentence
  words = sentence.split()

  for i in range(len(words)):
    if words[i][-1] == 's':
      words[i] = singularize(words[i])
    if '/' in words[i]:
      words[i]=str(ureg.parse_expression(words[i]))

  #print "The words: ", 
  #print words

  quantityBool = []
  for word in words:
    found = False
    if hasNumbers(word):
      found = True
    else:
      synsets = wordnet.synsets(word)
      for synset in synsets:
        if 'quantity' in synset.lexname:
          found = True
    quantityBool.append(found)
   
  #print quantityBool
  
  totalNum = 0
  quantities = [0,'whole']
  for i in range(len(quantityBool)):
    if quantityBool[i]:
      if hasNumbers(words[i]):
        quantities[0] = quantities[0] + float(words[i])
      else:
        quantities[1] = words[i]
    else:
      break
  words = words[i:]

  if quantities[0]==0:
    quantities[0] = 1
    
  quantities[0] = str(quantities[0])
  print quantities
  print words
  indices = []
  index = 0
  done = False
  isFluid = False
  for word in words:
    synsets = wordnet.synsets(word)
    #print synsets
    if len(synsets)<10:
      for synset in synsets:
        '''print "-" * 10
        print "Name:", synset.name
        print "Lexical Type:", synset.lexname
        print "Lemmas:", synset.lemma_names
        print "Definition:", synset.definition
        for example in synset.examples:
          print "Example:", example'''
        if 'liquid' in synset.definition or 'fluid' in synset.definition:
          isFluid = True
        if 'food' in synset.lexname or 'baking' in synset.name or 'plant' in synset.lexname :
          indices.append(index)
          break
    index = index + 1

  foods = indices
  print foods
  possibleWords = []
  for index in indices:
    if isFluid:
      possibleWords.append('^' + words[index] + '* NEAR/3 fluid')
    if index > 0:
      possibleWords.append('^' + words[index-1] + '* ' + words[index] + '*')
      possibleWords.append(words[index-1] + '* NEAR/3 ' + words[index] + '*')
    if index < len(words)-1:
      possibleWords.append('^' +words[index] + '* ' + words[index+1] + '*')
      possibleWords.append(words[index] + '* ' + words[index+1] + '*')
      possibleWords.append(words[index] + '* NEAR/3 ' + words[index+1] + '*')
      possibleWords.append(pluralize(words[index]) + ' NEAR/3 ' + words[index+1] + '*')
  for index in indices:  
    possibleWords.append('^' + words[index] + '*')
    possibleWords.append('^' + pluralize(words[index]))
    possibleWords.append(pluralize(words[index]) + ' NEAR/3 raw')
    possibleWords.append(pluralize(words[index]))
    
  print possibleWords


  with con:
      
      cur = con.cursor()    
      bestCandidate = 'no match'
      bestId = '-1'
      foundBestWord = False
      for possibleWord in possibleWords:
        print possibleWord
        if not foundBestWord:
          cur.execute('select ndb_no,shrt_desc,com_desc,length(com_desc)-length("'+possibleWord.replace('*','').split()[0] + '") as closest from data where com_desc match "' + possibleWord.replace('*','') + '" order by closest')

          row = cur.fetchone()
          if row is not None:
            ndb_no =  row[0].encode('utf-8')
            shrt_desc = row[1].encode('utf-8')
            bestCandidate = shrt_desc
            bestId = ndb_no
            foundBestWord = True
            break
      if not foundBestWord:
        for possibleWord in possibleWords:
          cur.execute('select c.ndb_no,shrt_desc,google_hits from ranking as r join data as c on r.ndb_no=c.ndb_no where shrt_desc match "'+possibleWord+'" order by google_hits desc')

          row = cur.fetchone()
          if row is not None:
            ndb_no =  row[0].encode('utf-8')
            shrt_desc = row[1].encode('utf-8')
            bestCandidate = shrt_desc
            bestId = ndb_no
            break


  food = bestCandidate
  print food
  print bestId
  foodId = bestId
  try:
    measurement = float(quantities[0])*ureg.parse_expression(quantities[1])
  except:
    measurement = float(quantities[0])*ureg.dimensionless

  with con:
    cur.execute('select ndb_no,amount,msre_desc,gm_wgt from weight where ndb_no like "'+foodId+'"')
    
    rows = cur.fetchall()
    
    foundMatch = False
    for row in rows:
      #print row
      try:
        if ureg.parse_expression(quantities[1]).to(ureg.parse_expression(row[2].encode('utf-8'))) is not None:
          foundMatch = True
      except:
        pass
      if foundMatch:
        dbMeasurement = float(row[1])*ureg.parse_expression(row[2].encode('utf-8'))
        measurement = measurement.to(ureg.parse_expression(row[2].encode('utf-8')))
        dbQuantity = row[2].encode('utf-8')
        dbGrams = row[3]
        break
    
    if not foundMatch:
      for row in rows:
        try:
          if ureg.parse_expression(row[2].encode('utf-8')):
            pass
        except:
          foundMatch = True
        if foundMatch:
          dbMeasurement = float(row[1])*ureg.dimensionless
          dbQuantity = row[2].encode('utf-8')
          dbGrams = row[3]
          break
  
  if 'teaspoon' in str(measurement) or 'tablespoon' in str(measurement):
    if measurement.magnitude>4:
      measurement = measurement.to(ureg.cups)
  
  if foundMatch:
    ratio = (measurement / dbMeasurement).magnitude
    grams = (ratio * float(dbGrams))

    '''
    print "Recipe called for ",
    print measurement,
    print " which is " + str(ratio) + " times the amount in database: ",
    print dbMeasurement,
    print "("+dbQuantity+")",
    print ". This equates to " + str(grams) + " grams"
    '''
    nutrition = getNutrition(foodId,grams/100.0,nutrition)
    
    return (food,foodId,measurement,grams,nutrition)
  else:
    return (food,'',float(quantities[0])*ureg.dimensionless,float(quantities[0]),nutrition)


def getNutrition(foodId,multiplier,nutrition):
    
  with con:
      
    cur = con.cursor()    

    cur.execute('select nutr_no,nutr_val from nutrition_data where ndb_no match "'+foodId+'"')
    
    rows = cur.fetchall()
    
    for row in rows:
      id = int(row[0])
      val = float(row[1])
      cur2 = con.cursor() 
      cur2.execute('select units,NutrDesc from nutr_def where nutr_no == "'+str(id)+'"')
      rows2 = cur2.fetchone()
      units = rows2[0]
      name = rows2[1]
      if ord(units[0])==65533:
        units = 'microgram'
      if units == 'IU':
        units = 'dimensionless'
      if name in nutrition.keys():
        nutrition[name.encode('utf-8')] = str(val*ureg.parse_expression(units)+ureg.parse_expression(nutrition[name.encode('utf-8')]))
      else:
        nutrition[name.encode('utf-8')] =str(val*ureg.parse_expression(units))
      
    
  return nutrition
      
        
  
#    extract_recipe(sys.argv[1])
'''
line_number = 0
with open("recipeitems-latest.json") as json_file:
    for line in json_file:
        line_number = line_number + 1
        if line_number == int(sys.argv[1]):
            try:
                # RegExp is needed here to remove the odd characters
                json_data = json.loads(re.sub(r'[^\x00-\x7F]+',' ', line))
                try:
                    html_text = main(json_data['url'])
                    data= extract_recipe(html_text)     
                    data_ingredients = extract_ingredients(html_text)
                except:
                    data='none'
            except:
                print "problem loading " + line
'''
def extract_recipe_main(url):
  finalString = ''
  try:
      html_text = main(url)
      data= extract_recipe(html_text)     
      (titleString,data_ingredients) = extract_ingredients(html_text)
  except:
      data='none'

  exclude = set(string.punctuation)
  #print '# ' + json_data['name'] + "\n"

  finalString = finalString + '# ' + titleString + '\n\n'
  finalString = finalString + '## Ingredients\n' 
  finalString = finalString + '-'*30
  finalString = finalString + "\n"
  nutrition  = {}
  start = time.time()
  for line in data_ingredients.split('\n'):
    if len(line)>2:
      finalString = finalString + line
      finalString = finalString + "\n"
      (food,foodId,measurement,grams,nutrition) = getFoodFromDatabase(line,nutrition)
      finalString = finalString + " - "
      finalString = finalString + str(measurement)
      finalString = finalString + " " + food + " (" + str(grams) + " g)\n\n"
   
  end = time.time()
  print end-start

  finalString = finalString + '-'*30
  finalString = finalString + "\n"
  '''
  ingredients = ''
  for ingredient in json_data['ingredients'].split('\n'):
    print " - " + ''.join(ch for ch in ingredient if ch not in exclude)
    ingredients = ingredients + ' ' + ''.join(ch for ch in ingredient if ch not in exclude)
  '''
  finalString = finalString + "\n"
  finalString = finalString + '## Directions\n' 

  finalString = finalString + data
  finalString = finalString + "\n"
  data = data.lower()
  data = data.replace('\n',' ')
  data = data.replace('one','1')
  data = data.replace('two','2')
  data = data.replace('three','3')
  data = data.replace('four','4')
  data = data.replace('five','5')
  data = data.replace('six','6')
  data = data.replace('seven','7')
  data = data.replace('eight','8')
  data = data.replace('nine','9')
  data = data.replace('ten','10')
  data = data.replace('twenty','20')
  data = data.replace('thirty','30')
  data = data.replace('forty','40')
  data = data.replace('fifty','50')
  data = data.replace('sixty','60')
  data = data.replace('overnight','12 hours')
  data = data.replace('few minute','3 minute')
  data = data.replace('few hour','3 hour')
  data = data.replace('another minute','1 minute')
  data = data.replace('several minute','4 minute')
  data = data.replace('one more minute','1 minute')
  data = data.replace('cook until','2 minute')
  data = data.replace('-',' ')
  data = ''.join(ch for ch in data if ch not in exclude)


  dataWords =  data.split()
  timeWords = ['minute','minutes','hour','hours']
  totalTime = 0*ureg.minute
  for timeWord in timeWords:
    timeI = [i for i, x in enumerate(dataWords) if x == timeWord]
    for i in timeI:
      try:
        totalTime = totalTime + int(dataWords[i-1])*ureg.parse_expression(dataWords[i])
      except:
        pass

  data = data + ' ' + data_ingredients
  dataWords =  data.split()
  cookingTimes = {'cut':1*ureg.minute,'knead':2*ureg.minute,'chop':1*ureg.minute,'food processor':2*ureg.minute,'slice':1*ureg.minute,'assemble':1*ureg.minute,'toss':1*ureg.minute,'filet':1*ureg.minute,'stuff':1*ureg.minute}
  for key in cookingTimes.keys():
    timesInData = [i for i, x in enumerate(dataWords) if x == key]
    totalTime = totalTime + len(timesInData)*cookingTimes[key]
    if len(timesInData)>0:
      finalString = finalString + "+"
      finalString = finalString + len(timesInData)*str(cookingTimes[key])
      finalString = finalString + " for " + key + "ing."
      finalString = finalString + "\n"
    
  if totalTime > 60*ureg.minute:
    finalString = finalString + "# Calculated time: "
    finalString = finalString + str(totalTime.to(ureg.hour))
    finalString = finalString + "\n"
  else:
    finalString = finalString + "# Calculated time: "
    finalString = finalString + str(totalTime)
    finalString = finalString + "\n"
  
  nutrition['Energy'] = str(ureg.parse_expression(nutrition['Energy']).to(ureg.kilocalorie))

  servings = int(ureg.parse_expression(nutrition['Energy']).magnitude/300)
  
  finalString = finalString +  "\n\n# Serving size is about " + str(servings) + "\n"
  
  finalString = finalString + "\n\n# Nutrition data (main)\n"
  importantNutrition = ['Energy','Protein','Total lipid (fat)','Carbohydrate, by difference','Sugars, total','Fiber, total dietary','Cholesterol']
  for key in importantNutrition:
    finalString = finalString +  key + ": " + nutrition[key]  + "\n"
  print "\n\n"
    
  finalString = finalString + "\n\n# Nutrition data (ALL)\n"
  for key in sorted(nutrition.iterkeys()):
    finalString = finalString +  key + ": " + nutrition[key]  + "\n"
  
  return finalString

extract_recipe_main('http://thepioneerwoman.com/cooking/2013/03/mixed-berry-shortcake/')
