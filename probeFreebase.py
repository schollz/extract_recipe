import json
import urllib
import sqlite3 as lite
from unidecode import unidecode

'''
last_ndb_no = '10909'
start = False
con = lite.connect('db')
with con:    
  cur = con.cursor()    
  cur.execute('select ndb_no,shrt_desc from food_des')
  rows = cur.fetchall()
  for row in rows:
    ndb_no =  row[0]
    print ndb_no
    if start:
      api_key = open(".freebase_api_key").read()
      service_url = 'https://www.googleapis.com/freebase/v1/mqlread'
      query = [{"name": [],"/food/food/usda_id": ndb_no}]
      params = {
              'query': json.dumps(query),
              'key': api_key
      }
      url = service_url + '?' + urllib.urlencode(params)
      urlOpen = urllib.urlopen(url)
      response = json.loads(urlOpen.read())
      if len(response['result'])>0:
        for planet in response['result']:
          print row[1] + unidecode(planet['name'][0])
          with open('ndb_no_freebase.txt','a') as f:
            f.write(ndb_no + "|" + unidecode(planet['name'][0]) + "\n")
    if last_ndb_no in ndb_no:
      start = True
'''

# Alter the database

con = lite.connect('db')
with con:
	cur = con.cursor()
	print "alter table food_des add column com_desc varchar(60);"
	with open('ndb_no_freebase.txt','rb') as f:
		for line in f:
			(ndb_no,com_desc) =  line.split('|')
			com_desc = com_desc.strip()
			command = 'update food_des set com_desc="%s" where ndb_no="%s";'%(com_desc,ndb_no)
			print command
			cur.execute(command)
