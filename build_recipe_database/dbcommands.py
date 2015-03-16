import sqlite3
import re
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S',
                    filename='log',
                    filemode='a')
                    
class DataBaseInvalidInput(Exception):
	pass
class DataBaseIntegrityError(Exception):
	pass

class DataBase:
	
	#takes path to database
	def __init__(self,path):
		self.conn = sqlite3.connect(path)
		self.conn.row_factory = sqlite3.Row #returns row objects instead of plain tuples
		self.c = self.conn.cursor()
		self.default_table_name = 'no_such_table'
	
	def close(self):
		self.conn.close()
		self.conn = None
		self.c = None	
	
	def insertLocationInfo( self,gps_lat,\
							gps_long,\
							description,\
							map_uuid):
		return self.addData(data={\
			'uuid':str(uuid.uuid3(uuid.NAMESPACE_DNS,map_uuid+'.'+description)),\
			'gps_lat':gps_lat,\
			'gps_long':gps_long,\
			'description':description,\
			'map_uuid':map_uuid\
			},table='location_info')


	'''
	GENERAL DATA COMMANDS
	'''		
	
	
	#data given as tuple of values in order of table columns
	#returns rowid of new row or -1 if integrity error
	def addData(self,data,table):
		try:
			#None is for the primary key which auto increments
			if type(data) is list or type(data) is tuple:
				self.c.execute('INSERT INTO %s VALUES (%s)'%(table,('?,'*len(data))[:-1]),data)
			elif type(data) is dict:
				keys = list(data.keys())
				#keys = data.keys()
				try:
					values = [data[k] for k in keys]
					#values = list(data.values())
					#values = data.values()
				except KeyError:
					raise DataBaseInvalidInput('sanitized column names don\'t match given column names')
				self.c.execute('INSERT INTO %s (%s) VALUES (%s)'%(table , ','.join(keys) , ','.join(['?']*len(data))) , values)
			else:
				raise Exception('invalid input type: %s'%type(data))
			id = self.c.lastrowid
			#remember to commit changes so we don't lock the db!
			self.conn.commit()
			return id
		except sqlite3.IntegrityError as e:
			raise DataBaseIntegrityError('%s' %e)


		
	def removeData(self,id,table):
		self.c.execute('DELETE FROM %s WHERE id=?'%table,(id,))
		self.conn.commit()
		
	#parameters is a dictionary of key : value
	#will run a query using WHERE key = value
	#if parameters is {} then returns all
	#so example: getData({'id':3},'maps') returns
	#array of all maps with id = 3.
	#will throw errors if table name is bad
	#also make sure NOT to use arbitrary things here since statements are directly thrown into
	#sqlite, i.e. injections possible. use carefully. No client data here, or if so, make sure it's
	#properly validated
	def getData(self,table,parameters = {}):
		query = "SELECT * FROM %s" %table
		keys = parameters.keys()
		query_extra = ' AND '.join(k + ' = ?' for k in keys)
		query += (' WHERE ' + query_extra) if query_extra is not '' else ''
		self.c.execute(query,[parameters[k] for k in keys])
		return self.c.fetchall()
		
	def contains(self,id,table):
		self.c.execute('SELECT EXISTS(SELECT 1 FROM %s WHERE id=(?) LIMIT 1)'%table,(id,))
		return self.c.fetchone()[0] is 1
	
	
	'''
	
	GENERAL TABLE COMMANDS - USE WITH CAUTION
	
	'''
	
	def showTables(self):
		return [a[0] for a in self.c.execute("SELECT name FROM sqlite_master WHERE type='table';")]
		
	
	#returns true if table exists
	def tableExists(self,table_name):
		self.c.execute('SELECT EXISTS(SELECT 1 FROM sqlite_master WHERE type="table" AND name=? LIMIT 1)',(table_name,))
		return not self.c.fetchone()[0] is 0
	
	#builds table if doesn't already exist
	#-a little sketchy
	def createTable(self,table_data):
		logger = logging.getLogger('dbcommands.createTable')
		if self.tableExists(table_data):
			return False
		else:
			self.c.execute('CREATE TABLE %s;' % table_data)
			self.conn.commit()
			logger.debug('Table created')
			return True
	#drops table
	#-a little sketchy
	def dropTable(self,table):
		if self.tableExists(table):
			self.c.execute('DROP TABLE %s' % table)
			self.conn.commit()
			return True
		else:
			return False

	#prints a description of columns
	def showColumns(self,table):
		names = self.columnNames(table)
		types = self.columnTypes(table)
		for i in range(len(names)):
			print("%s - %s" % (names[i],types[i]))
			
	#list of column names
	def columnNames(self,table):
		return [r[1] for r in self.c.execute('PRAGMA table_info(%s)' % table)]
	
	#type of data stored in column
	def columnTypes(self,table):
		return [r[2] for r in self.c.execute('PRAGMA table_info(%s)' % table)]

    
    
def setupDatabase():
	# Start logger
	logger = logging.getLogger('databaseSetup.setupDatabase')
	logger.info('Setting up database...')
	DB = DataBase(DATABASE_PATH)

	#
	#SET UP INITIAL TABLES
	#

	#resources TABLE
	if not DB.tableExists('resources'):
		logger.warning('"resources" table not found')
		logger.info('Creating "resources" table...')
		DB.createTable('resources ('\
			+'id INTEGER PRIMARY KEY AUTOINCREMENT, '\
		#	+'uuid TEXT UNIQUE,'\
			+'uuid TEXT,'\
			+'type TEXT,'\
			+'pickle BLOB '\
			+')')
	else:
		logger.debug('Table "resources" found')

	logger.info('Database ready')

