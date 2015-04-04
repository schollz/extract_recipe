from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import Levenshtein
import operator
import time
import threading
from itertools import combinations
from multiprocessing import Process
import cPickle as pickle
import os
import subprocess


foo = subprocess.Popen(['grep','-c','processor','/proc/cpuinfo'], stdout=subprocess.PIPE)
out, err = foo.communicate()
NUM_PROCESSORS = int(out.decode('utf-8').strip())
print('Multiprocessing support with ' + str(NUM_PROCESSORS) + ' cores')

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


def worker(num,total,foodStrings):
  stringMatches = []
  partialList = {}
  """thread worker function"""
  for foodString in foodStrings:
    for (i,key) in enumerate(foodList.keys()):
      if i%total==num:
        leven1 = fuzz.token_set_ratio(key,foodString)
        leven2 = Levenshtein.ratio(foodString,key)
        if leven2>0.5:
          stringMatches.append((key,foodList[key],leven1,leven2))
  pickle.dump(stringMatches,open(str(num)+'.p','wb'))
  return 
  


def getStringMatches(foodString):
  print(foodString)
  foodString = foodString.replace(',',' ').lower()
  foodStrings = []
  foodStrings.append(foodString)
  foodWords = foodString.split()
  if len(foodWords)>2:
    otherFoodWords = combinations(foodWords,2)
    for words in otherFoodWords:
      foodStrings.append(' '.join(words))
  if len(foodWords)>3:
    otherFoodWords = combinations(foodWords,3)
    for words in otherFoodWords:
      foodStrings.append(' '.join(words))
  stringMatches = []
  partialList = {}
  
 
  processes = []
  totalProcesses = NUM_PROCESSORS
  for i in range(totalProcesses):
    t = Process(target=worker, args=(i,totalProcesses,foodStrings,))
    processes.append(t)
  for t in processes:
    t.start()
  for t in processes:
    t.join()
    
  for i in range(totalProcesses):
    foo = pickle.load(open(str(i)+'.p','rb'))
    stringMatches = stringMatches + foo
    os.system('rm ' + str(i)+'.p')
    
  
  '''
  for foodString in foodStrings:
    for (i,key) in enumerate(foodList.keys()):
      partialList[key] = fuzz.token_set_ratio(key,foodString)

    foo = sorted(partialList.items(), key=operator.itemgetter(1),reverse=True)[:100]
    for result in foo:
      leven=Levenshtein.ratio(foodString,result[0])
      if leven>0.5:
        stringMatches.append((result[0],foodList[result[0]],result[1],leven))
  '''
  matches = (sorted(stringMatches, key=operator.itemgetter(2, 3), reverse=True))
  return matches
  
'''
t = time.time() 
print(getStringMatches('yellow corn')[:30])
print(time.time()-t)
'''

