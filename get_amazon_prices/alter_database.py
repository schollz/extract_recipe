import json
import urllib
import sqlite3 as lite
from unidecode import unidecode

# Alter the database

con = lite.connect('../db')
with con:
  cur = con.cursor()
  print "alter table food_des add column price real;"
  print "alter table food_des add column unit varchar(60);"
  with open('ndb_mean_std_unit.txt','rb') as f:
    for line in f:
      (ndb_no,mean,stdev,unit) =  line.split('^')
      command = 'update food_des set unit="%s" where ndb_no="%s";'%(unit,ndb_no)
      print command
      cur.execute(command)
      command = 'update food_des set price=%s where ndb_no="%s";'%(mean,ndb_no)
      print command
      cur.execute(command)
  # Eggs
  command = 'update food_des set price=0.005 where ndb_no="01123";'
  cur.execute(command)
  # Milk
  command = 'update food_des set price=0.000792 where ndb_no="01077";'
  cur.execute(command)
  # Sliced Cheese
  command = 'update food_des set price=0.030277 where ndb_no="01270";'
  cur.execute(command)
  

