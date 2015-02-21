'''
This program uses the AmazonAPI to gather the top results for grocery items 
and saves them according to their USDA NDB_NO identifier. 

Use the tor_wrapper if you get blocked from making too many calls.
'''

from amazon.api import AmazonAPI
from unidecode import unidecode


usingTor = True

# Set to True if using the first time, otherwise use false
start = False

if usingTor:
  import socks
  import socket
  socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
  socket.socket = socks.socksocket


AMAZON_ASSOC_TAG='XX'
# https://console.aws.amazon.com/iam/home#security_credential
AMAZON_ACCESS_KEY='XX'
AMAZON_SECRET_KEY='XX'


amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)


if not start:
  with open('lastNDB','rb') as f:
    for line in f:
      lastNDB = line.strip()

with open('../get_freebase_num/ndb_no_freebase.txt','rb') as f:
  for line in f:
    (ndb_no,searchTerm)=line.split('|')
    print ndb_no
    print searchTerm
    if start:
      products = amazon.search(Keywords=searchTerm, SearchIndex='Grocery')
      knownUnit = None
      prices = []
      units = {}
      for i, product in enumerate(products):
        try:
          if product.price_and_currency[0] is not None:
            with open('ndb_nos/' + ndb_no + '.txt','a') as f:
              f.write("{0}\t{2}\t{1}\n".format(i, unidecode(product.title),product.price_and_currency[0]))
        except:
          pass
      with open('lastNDB','a') as f:
        f.write(ndb_no + '\n')
    else:
      if ndb_no == lastNDB:
        start = True
      
      
