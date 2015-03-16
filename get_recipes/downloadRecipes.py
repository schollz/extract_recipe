import json
import os
import urllib2
import urllib
import html2text
from unidecode import unidecode
import time
import urllib
import logging
import os
import os.path
import sys
import threading



if os.path.isfile('recipeitems-latest.json'):
  pass
else:
  os.system('wget http://openrecipes.s3.amazonaws.com/recipeitems-latest.json.gz')
  os.system('gunzip recipeitems-latest.json.gz')

if not os.path.exists('recipes'):
    os.makedirs('recipes')

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S',
                    filename='log',
                    filemode='a')
                                  
def get_url_markdown(baseurl,start,increment):
  '''
  opener = urllib2.build_opener()
  opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0')]
  try:
    j = opener.open(baseurl)
  except:
    return None
  data = j.read()
  '''
  urlHandler = urllib2.urlopen(baseurl)
  data = urlHandler.read()
  '''
  os.system('wget -O temp' + str(start)+"_"+str(increment) + ' ' + baseurl)
  data = open('temp' + str(start)+"_"+str(increment),'rU').read()
  '''
  h = html2text.HTML2Text()
  h.ignore_links = True
  h.ignore_images = True
  h.body_width = 10000
  data = h.handle(unidecode(unicode(data,errors='ignore')))
  return unidecode(data)
  
def worker(start,increment):
  logger = logging.getLogger('worker'+str(start)+"_"+str(increment))      
  """thread worker function"""
  print 'Worker: %s/%s' % (start,increment)
  indexFile = 'recipes/index'+str(start)+"_"+str(increment)+'.txt'
  lastLine = ""
  if os.path.isfile(indexFile):
      with open(indexFile,'rb') as f:
          for line in f:
              lastLine = line
      lastfileNum = int(lastLine.split()[0])
  else:
      lastfileNum = -1

  fileNum = 0
  t = time.time()
  with open('recipeitems-latest.json','rb') as f:
    for line in f:
      fileNum = fileNum + 1
      if fileNum % increment == start:
        folderSave = str(int(fileNum/500))
        if not os.path.exists('recipes/' + folderSave):
            os.makedirs('recipes/' + folderSave)

        if fileNum>lastfileNum:
          recipe = json.loads(line)
          logger.info(str(fileNum) + "\t" + recipe['url'] + '\t' + recipe['name'])
          t=time.time()
          recipeMD = get_url_markdown(recipe['url'],start,increment)
          logger.info('%s seconds' % str(round(time.time()-t,1)))
          if recipeMD is not None:
            with open('recipes/' + folderSave + '/' + str(fileNum) + '.md','wb') as g:
              g.write(recipeMD)
            #os.system('bzip2 ' + 'recipes/' + folderSave + '/' + str(fileNum) + '.md')        
            with open(indexFile,'a') as g:
              g.write(str(fileNum) + "\t" + recipe['url'] + '\t' + unidecode(recipe['name']) + '\n')
          else:
            with open(indexFile,'a') as g:
              g.write(str(fileNum) + "\t" + recipe['url'] + '\t' + 'None' + '\n')      
  return
 
threads = []
numThreads = 15
for i in range(numThreads):
    t = threading.Thread(target=worker, args=(i,numThreads,))
    threads.append(t)
    t.start()