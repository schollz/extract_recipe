from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import Levenshtein
import operator
import time
import threading


foodList = {}
with open('long_desc.csv','r') as f:
  for line in f:
    foo = line.strip().split('\t')
    food=foo[0]
    ndb_no=foo[1]
    foodList[food.replace(',','').lower()]=str(ndb_no)
with open('com_desc.csv','r') as f:
  for line in f:
    foo = line.strip().split('\t')
    food=foo[0]
    ndb_no=foo[1]
    foodList[food.lower()] =str(ndb_no)
with open('shrt_desc.csv','r') as f:
  for line in f:
    foo = line.strip().split('\t')
    food=foo[0]
    ndb_no=foo[1]
    foodList[food.replace(',',' ').lower()]=str(ndb_no)


def worker(num,total,foodString):
  global partialList
  """thread worker function"""
  for (i,key) in enumerate(foodList.keys()):
    if i % total == num:
      partialList[key] = fuzz.token_set_ratio(key,foodString.replace(',',''))
  return
   
def getStringMatches(foodString):
  print(foodString)
  foodString = foodString.replace(',',' ').lower()
  stringMatches = []
  partialList = {}
  '''
  threads = []
  totalThreads = 3
  for i in range(totalThreads):
    t = threading.Thread(target=worker, args=(i,totalThreads,foodString,))
    threads.append(t)
    t.start()
    t.join()
  '''
  for (i,key) in enumerate(foodList.keys()):
    partialList[key] = fuzz.token_set_ratio(key,foodString)

  foo = sorted(partialList.items(), key=operator.itemgetter(1),reverse=True)[:100]
  for result in foo:
    leven=Levenshtein.ratio(foodString,result[0])
    if leven>0.5:
      stringMatches.append((result[0],foodList[result[0]],result[1],leven))
  matches = (sorted(stringMatches, key=operator.itemgetter(2, 3), reverse=True))
  return matches
  

