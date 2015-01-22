from nltk.corpus import wordnet
import sys
from pattern.en import singularize
import string
exclude = set(string.punctuation)

for word in sys.argv[1:]:
  word = ''.join(ch for ch in word if ch not in exclude)
  word = word.lower()
  word = singularize(word)
  synsets = wordnet.synsets(word)
  foundLexname = False
  for synset in synsets:
    if 'food' in synset.lexname:
      print 'food ',
      foundLexname = True
    if 'quantity' in synset.lexname:
      print 'quantity ',
      foundLexname = True
  if not foundLexname:
    print 'none ',
    '''
    print "-" * 10
    print "Name:", synset.name
    print "Lexical Type:", synset.lexname
    print "Lemmas:", synset.lemma_names
    print "Definition:", synset.definition
    for example in synset.examples:
      print "Example:", example
    ''' 

