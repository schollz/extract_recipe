import json
import urllib
import sqlite3 as lite
con = lite.connect('db')
with con:    
  cur = con.cursor()    
  cur.execute('select ndb_no from food_des')
  rows = cur.fetchall()
  for row in rows:
    ndb_no =  row[0]

    api_key = open(".freebase_api_key").read()
    service_url = 'https://www.googleapis.com/freebase/v1/mqlread'
    query = [{"name": [],"/food/food/usda_id": ndb_no}]
    params = {
            'query': json.dumps(query),
            'key': api_key
    }
    url = service_url + '?' + urllib.urlencode(params)
    urlOpen = urllib.urlopen(url)
    if urlOpen.code == 200:
      response = json.loads(urlOpen.read())
      if len(response['result'])>0:
        for planet in response['result']:
          with open('ndb_no_freebase.txt','a') as f:
            f.write(ndb_no + "|" + ','.join(planet['name']) + "\n")
    else:
      print "ERROR ON " + ndb_no
