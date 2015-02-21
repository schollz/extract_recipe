from amazon.api import AmazonAPI
from pint import UnitRegistry
ureg = UnitRegistry()
from unidecode import unidecode
import numpy as np
import pprint

import socks
import socket
socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
socket.socket = socks.socksocket

def hasNumbers(inputString):
  return any(char.isdigit() for char in inputString)

def extractUnits(title):
  unitExpression = None
  multiplier = 1
  title = title.replace('-',' ')
  title = title.replace('$','')
  title = title.replace('%','')
  title = title.replace(')','')
  title = title.replace('(','')
  words = title.lower().split()
  print words
  numIndicies = []
  for i in range(len(words)):
    if hasNumbers(words[i]):
      words[i]=str(ureg.parse_expression(words[i]))
      numIndicies.append(i)
      if i>1:
        if 'of' == words[i-1]:
          if 'pack' == words[i-2] or 'count' == words[i-2]:
            multiplier = int(words[i])
    else:
      words[i] = words[i].replace(',','')
      words[i] = words[i].replace('.','')
      
  for i in range(len(words)-1):
    try:
      if hasNumbers(words[i]):
        unitExpression = ureg.parse_expression(words[i] + ' ' + words[i+1])
    except:
      pass
  print multiplier
  print unitExpression

AMAZON_ASSOC_TAG='XX'
# https://console.aws.amazon.com/iam/home#security_credential
AMAZON_ACCESS_KEY='XX'
AMAZON_SECRET_KEY='XX'


amazon = AmazonAPI(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)

start = False

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
      
      



'''
title = unidecode(product.title)
try:
  extractedWeight = extractUnits(title)
  print product.price_and_currency[0]/extractedWeight
  unitType = str(extractedWeight.dimensionality)
  if unitType in units:
    units[unitType] = units[unitType] + 1
  else:
    units[unitType] = 1
  pricePerProduct = product.price_and_currency[0]/extractedWeight
  prices.append(pricePerProduct)
except:
  pass
'''
'''
np.set_printoptions(precision=2,linewidth=100000)
print prices
print units
'''
