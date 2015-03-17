import sqlite3
import re
import logging

def is_number(s):
  try:
      float(s)
      return True
  except ValueError:
      return False

def formatIngredientKey(key):
  key = key.strip()
  key = key.lower()
  key = key.replace(':','_')
  key = key.replace('-','_')
  key = key.replace(',','_')
  key = key.replace('+','_')
  key = key.replace(')','_')
  key = key.replace('(','_')
  key = key.split()
  key = '_'.join(key)
  key = key.replace('__','_')
  key = key.replace('__','_')
  key = key.replace('__','_')
  key = key.replace('__','_')
  if key[0] == '_':
    key = key[1:]
  if key[-1] == '_':
    key = key[0:-2]
  if key[0] == '_':
    key = key[1:]
  if key[-1] == '_':
    key = key[0:-2]
  if key[0] == '_':
    key = key[1:]
  if key[-1] == '_':
    key = key[0:-2]
  if is_number(key[0]):
    key = 'i' + key
  return key
                    
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
  
  def updateIngredient(self,target,value,row):
    self.c.execute('update recipes set %s=%s where id=%s'%(formatIngredientKey(target),str(value),str(row)))
    self.conn.commit()

  def addIngredient(self,recipe_id,ingredient_uuid,actual,measurement,description,ndb_no,cost,grams):
    return self.addData(data={\
      'recipe_id':recipe_id,\
      'ingredient_uuid':ingredient_uuid,\
      'actual':actual,\
      'measurement':measurement,\
      'description':description,\
      'ndb_no':ndb_no,\
      'cost':cost,\
      'grams':grams\
      },table='ingredients')
      
      
  def newRecipe(self,title,url,source,directions,time,total_cost,total_cost_per_serving,serving_size,total_grams,num_ingredients):
    return self.addData(data={\
      'title':title,\
      'url':url,\
      'source':source,\
      'directions':directions,\
      'time':time,\
      'total_cost':total_cost,\
      'total_cost_per_serving':total_cost_per_serving,\
      'serving_size':serving_size,\
      'total_grams':total_grams,\
      'num_ingredients':num_ingredients,\
      'protein':0,\
      'total_lipid_fa':0,\
      'carbohydrate_by_difference':0,\
      'ash':0,\
      'energy':0,\
      'starch':0,\
      'sucrose':0,\
      'glucose_dextros':0,\
      'fructose':0,\
      'lactose':0,\
      'maltose':0,\
      'alcohol_ethyl':0,\
      'water':0,\
      'adjusted_protein':0,\
      'caffeine':0,\
      'theobromine':0,\
      'sugars_total':0,\
      'galactose':0,\
      'fiber_total_dietary':0,\
      'calcium_ca':0,\
      'iron_fe':0,\
      'magnesium_mg':0,\
      'phosphorus_p':0,\
      'potassium_k':0,\
      'sodium_na':0,\
      'zinc_zn':0,\
      'copper_cu':0,\
      'fluoride_f':0,\
      'manganese_mn':0,\
      'selenium_se':0,\
      'vitamin_a_iu':0,\
      'retinol':0,\
      'vitamin_a_rae':0,\
      'carotene_beta':0,\
      'carotene_alpha':0,\
      'vitamin_e_alpha_tocophero':0,\
      'vitamin_d':0,\
      'vitamin_d2_ergocalcifero':0,\
      'vitamin_d3_cholecalcifero':0,\
      'vitamin_d_d2_d':0,\
      'cryptoxanthin_beta':0,\
      'lycopene':0,\
      'lutein_zeaxanthin':0,\
      'tocopherol_beta':0,\
      'tocopherol_gamma':0,\
      'tocopherol_delta':0,\
      'tocotrienol_alpha':0,\
      'tocotrienol_beta':0,\
      'tocotrienol_gamma':0,\
      'tocotrienol_delta':0,\
      'vitamin_c_total_ascorbic_acid':0,\
      'thiamin':0,\
      'riboflavin':0,\
      'niacin':0,\
      'pantothenic_acid':0,\
      'vitamin_b_6':0,\
      'folate_total':0,\
      'vitamin_b_12':0,\
      'choline_total':0,\
      'menaquinone_4':0,\
      'dihydrophylloquinone':0,\
      'vitamin_k_phylloquinon':0,\
      'folic_acid':0,\
      'folate_food':0,\
      'folate_dfe':0,\
      'betaine':0,\
      'tryptophan':0,\
      'threonine':0,\
      'isoleucine':0,\
      'leucine':0,\
      'lysine':0,\
      'methionine':0,\
      'cystine':0,\
      'phenylalanine':0,\
      'tyrosine':0,\
      'valine':0,\
      'arginine':0,\
      'histidine':0,\
      'alanine':0,\
      'aspartic_acid':0,\
      'glutamic_acid':0,\
      'glycine':0,\
      'proline':0,\
      'serine':0,\
      'hydroxyproline':0,\
      'vitamin_e_added':0,\
      'vitamin_b_12_added':0,\
      'cholesterol':0,\
      'fatty_acids_total_trans':0,\
      'fatty_acids_total_saturated':0,\
      'i4_0':0,\
      'i6_0':0,\
      'i8_0':0,\
      'i10_0':0,\
      'i12_0':0,\
      'i14_0':0,\
      'i16_0':0,\
      'i18_0':0,\
      'i20_0':0,\
      'i18_1_undifferentiated':0,\
      'i18_2_undifferentiated':0,\
      'i18_3_undifferentiated':0,\
      'i20_4_undifferentiated':0,\
      'i22_6_n_3_dh':0,\
      'i22_0':0,\
      'i14_1':0,\
      'i16_1_undifferentiated':0,\
      'i18_4':0,\
      'i20_1':0,\
      'i20_5_n_3_ep':0,\
      'i22_1_undifferentiated':0,\
      'i22_5_n_3_dp':0,\
      'phytosterols':0,\
      'stigmasterol':0,\
      'campesterol':0,\
      'beta_sitosterol':0,\
      'fatty_acids_total_monounsaturated':0,\
      'fatty_acids_total_polyunsaturated':0,\
      'i15_0':0,\
      'i17_0':0,\
      'i24_0':0,\
      'i16_1_t':0,\
      'i18_1_t':0,\
      'i22_1_t':0,\
      'i18_2_t_not_further_defined':0,\
      'i18_2_i':0,\
      'i18_2_t_t':0,\
      'i18_2_clas':0,\
      'i24_1_c':0,\
      'i20_2_n_6_c_c':0,\
      'i16_1_c':0,\
      'i18_1_c':0,\
      'i18_2_n_6_c_c':0,\
      'i22_1_c':0,\
      'i18_3_n_6_c_c_c':0,\
      'i17_1':0,\
      'i20_3_undifferentiated':0,\
      'fatty_acids_total_trans_monoenoic':0,\
      'fatty_acids_total_trans_polyenoic':0,\
      'i13_0':0,\
      'i15_1':0,\
      'i18_3_n_3_c_c_c_al':0,\
      'i20_3_n_3':0,\
      'i20_3_n_6':0,\
      'i20_4_n_6':0,\
      'i18_3i':0,\
      'i21_5':0,\
      'i22_4':0,\
      'i18_1_11_t_18_1':0\
      },table='recipes')


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
    
  def getRecipeIDfromURL(self,url):
    self.c.execute('SELECT id FROM recipes WHERE url="%s" LIMIT 1'%url)
    return self.c.fetchone()[0]
  
  
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



