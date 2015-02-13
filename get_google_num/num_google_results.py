import re
import datetime
import requests
from bs4 import BeautifulSoup
import progressbar
import os.path

REGEX = r'About (.*) results'

def number_of_search_results(key):
    def extract_results_stat(url):
        headers = { 
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/21.0'
        }
        search_results = requests.get(url, headers=headers, allow_redirects=True)
        soup = BeautifulSoup(search_results.text)
        result_stats = soup.find(id='resultStats')
        m = re.match(REGEX, result_stats.text)
        # print m.group(1)
        return int(m.group(1).replace(',',''))

    google_main_url = 'https://www.google.co.in/search?q=' + key
    google_news_url = 'https://www.google.co.in/search?hl=en&gl=in&tbm=nws&authuser=0&q=' + key
    return extract_results_stat(google_main_url)
    
numLines = 0
with open('food_des.txt') as f:
  for line in f:
    if len(line)>3:
      numLines = numLines + 1

print "There are " + str(numLines) + " foods"
bar = progressbar.ProgressBar(maxval=numLines,widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])

startLine = 0
if os.path.isfile('finished.txt'):
  with open('finished.txt') as f:
    for line in f:
      if len(line)>0:
        startLine = int(line.strip())
print startLine

i = 0
with open('food_des.txt') as f:
  for line in f:
    if len(line)>3:
      i = i+1
      bar.update(i)
      if i>startLine:
        (ndb_no,long_des) = line.split('|')
        try:
          num=number_of_search_results(long_des)
          with open("ndb_no-long_des-num.txt", "a") as myfile:
            myfile.write(ndb_no + "|" + long_des.strip() + "|" + str(num) + "\n")
          with open("finished.txt","a") as myfile:
            myfile.write(str(i) + "\n")
        except:
          with open("error.txt","a") as myfile:
            myfile.write(str(i) + "\n")        
    
'''
d_view = [ (v,k) for k,v in foods.iteritems() ]
d_view.sort(reverse=True) # natively sort tuples by first element
for v,k in d_view:
    print "%s: %d" % (k,v)
    '''