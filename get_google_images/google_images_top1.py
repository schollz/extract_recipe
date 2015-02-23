'''
This program grabs the first google image for a given search

Use the tor_wrapper if you get blocked from making too many calls.
'''

from unidecode import unidecode
import urllib2
import json
import sqlite3 as lite
con = lite.connect('../db')

usingTor = False



if usingTor:
  import socks
  import socket
  socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
  socket.socket = socks.socksocket


def getImage(searchString):
  opener = urllib2.build_opener()
  opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0')]
  j = opener.open('https://ajax.googleapis.com/ajax/services/search/images?v=1.0&q='+searchString.replace(' ','%20'))
  data = j.read()
  jsonData = json.loads(data)
  try:
    data = jsonData['responseData']['results'][0]['url']
  except:
    return False
  return data

imageUrl = getImage('Cheese, blue')
if imageUrl:
  print imageUrl