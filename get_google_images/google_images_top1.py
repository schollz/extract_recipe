'''
This program grabs the first google image for a given search

Use the tor_wrapper if you get blocked from making too many calls.
'''

from unidecode import unidecode
import urllib2
import urllib
import json
import sqlite3 as lite
con = lite.connect('../db')

start = False
usingTor = True
try:
  with open('stateFile','rb') as f:
    for line in f:
      lastState = line.strip()
except:
  lastState = 'none'
  start = True
  
print lastState

if usingTor:
  import socks
  import socket
  socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
  socket.socket = socks.socksocket


def getImage(searchString):
  opener = urllib2.build_opener()
  opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0')]
  j = opener.open('https://ajax.googleapis.com/ajax/services/search/images?v=1.0&q='+urllib.quote_plus(searchString))
  data = j.read()
  jsonData = json.loads(data)
  try:
    data = jsonData['responseData']['results'][0]['url']
    try:
      data2 = jsonData['responseData']['results'][1]['url']
    except:
      data2 = False
    return (data,data2,jsonData['responseStatus']==200)
  except:
    return (False,False,jsonData['responseStatus']==200)
  


  
with con:
  cur = con.cursor()    
  cur.execute('select ndb_no,long_desc from food_des order by ndb_no')
  rows = cur.fetchall()
  print len(rows)

for row in rows:
  if start:
    imageUrl = False
    while not imageUrl:
      (imageUrl,imageUrl2,goodResponse) = getImage(row[1])
      if not goodResponse:
        print "restarting tor..."
        os.system('/etc/init.d/tor restart')
    print "[" + str(goodResponse) + "] Getting " + imageUrl + " for '" + row[1] + "'"
    suffix = "jpg"
    suffixes = ['gif','jpeg','jpg','png','bmp']
    for i in suffixes:
      if i in imageUrl:
        suffix = i
    try:
      urllib.urlretrieve(imageUrl,"images/" + row[0]+"." + suffix)
    except:
      imageUrl = imageUrl2
      print "[" + str(goodResponse) + "] Getting " + imageUrl + " for '" + row[1] + "'"
      suffix = "jpg"
      suffixes = ['gif','jpeg','jpg','png','bmp']
      for i in suffixes:
        if i in imageUrl:
          suffix = i
      urllib.urlretrieve(imageUrl,"images/" + row[0]+"." + suffix)
    
    with open('stateFile','a') as f:
      f.write(row[0] + "\n")
  if row[0]==lastState:
    start=True
    