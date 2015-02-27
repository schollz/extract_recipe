import json
import os
import urllib2
import urllib
import html2text
from unidecode import unidecode
import time
import urllib

def get_url_markdown(baseurl):
  opener = urllib2.build_opener()
  opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0')]
  j = opener.open(baseurl)
  data = j.read()

  h = html2text.HTML2Text()
  h.ignore_links = True
  h.ignore_images = True
  h.body_width = 10000
  data = h.handle(unidecode(unicode(data,errors='ignore')))
  return unidecode(data)
  
try:
  with open('recipes/index.txt','rb') as f:
    for line in f:
      lastfileNum = int(line.split()[0])
except:
  lastfileNum = 0
fileNum = 0
t = time.time()
with open('recipeitems-latest.json','rb') as f:
  for line in f:
    fileNum = fileNum + 1
    if fileNum>lastfileNum:
      recipe = json.loads(line)
      print str(fileNum) + "\t" + recipe['url'] + '\t' + recipe['name']
        
      with open('recipes/' + str(fileNum) + '.md','wb') as g:
        g.write(get_url_markdown(recipe['url']))
        
      with open('recipes/index.txt','a') as g:
        g.write(str(fileNum) + "\t" + recipe['url'] + '\t' + unidecode(recipe['name']) + '\n')
    if fileNum % 10 == 0:
      u = time.time()
      print str(round((u-t)/10,1)) + ' seconds per result'
      t = u
