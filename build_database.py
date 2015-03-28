from dbcommands import *
import logging
import json
from recipe import *
import os.path

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M:%S',
                    filename='log',
                    filemode='a')

DATABASE_PATH = 'cookbook'
DB = DataBase(DATABASE_PATH)

  

'''
recipes = "'title':title,\\\n"
recipes = recipes + "'url':url,\\\n"
recipes = recipes + "'source':source,\\"
recipes = recipes + "'directions':directions,\\\n"
recipes = recipes + "'time':time,\\\n"
recipes = recipes + "'total_cost':total_cost,\\\n"
recipes = recipes + "'total_cost_per_serving':total_cost_per_serving,\\\n"
recipes = recipes + "'serving_size':serving_size,\\\n"
recipes = recipes + "'total_grams':total_grams,\\\n"
recipes = recipes + "'num_ingredients':num_ingredients,\\\n"
with open('list_of_nutrients.txt','r') as f:
  for line in f:
    recipes = recipes + "'" + formatIngredientKey(line) + "':0,\\\n"
print(recipes)
'''


logger = logging.getLogger('build_database.createTable')
recipes = 'recipes (id INTEGER PRIMARY KEY AUTOINCREMENT, '
recipes = recipes + 'title TEXT, '
recipes = recipes + 'url TEXT UNIQUE, '
recipes = recipes + 'source TEXT, '
recipes = recipes + 'directions TEXT, '
recipes = recipes + 'time TEXT, '
recipes = recipes + 'total_cost REAL, '
recipes = recipes + 'total_cost_per_serving REAL, '
recipes = recipes + 'serving_size REAL, '
recipes = recipes + 'total_grams REAL, '
recipes = recipes + 'num_ingredients INTEGER, '
with open('list_of_nutrients.txt','r') as f:
  for line in f:
    recipes = recipes +  formatIngredientKey(line) + " REAL,"
recipes = recipes[:-1] + ')'

if not DB.tableExists('recipes'):
  logger.warning('"recipes" table not found')
  logger.info('Creating "recipes" table...')
  DB.createTable(recipes)
else:
  logger.debug('Table "recipes" found')
  

logger = logging.getLogger('build_database.createIngredients')
recipes = 'ingredients (id INTEGER PRIMARY KEY AUTOINCREMENT, '
recipes = recipes + 'recipe_id INTEGER, '
recipes = recipes + 'ingredient_uuid TEXT UNIQUE, '
recipes = recipes + 'actual TEXT, '
recipes = recipes + 'measurement TEXT, '
recipes = recipes + 'description TEXT, '
recipes = recipes + 'ndb_no TEXT, '
recipes = recipes + 'cost REAL, '
recipes = recipes + 'grams REAL)'

if not DB.tableExists('ingredients'):
  logger.warning('"ingredients" table not found')
  logger.info('Creating "ingredients" table...')
  DB.createTable(recipes)
else:
  logger.debug('Table "ingredients" found')

'''
	def newRecipe( self,\
              title,\
              url,\
              source,\
              directions,\
              time,\
              total_cost,\
              total_cost_per_serving,\
              serving_size,\
              total_grams,\
							num_ingredients):
'''

'''
      'recipe_id':recipe_id,\
      'ingredient_uuid':ingredient_uuid,\
      'actual':actual,\
      'measurement':measurement,\
      'description':description,\
      'ndb_no':ndb_no,\
      'cost':cost,\
      'grams':grams\
'''
startNum = 9620
logger = logging.getLogger('build_database.building')
with open('get_recipes/recipes/index0_10.txt','r') as f:
  for line in f:
    #try:
    try:
      data = line.strip().split()
      recipeNum = int(data[0])
      url = data[1]
      title = ' '.join(data[2:])
    except:
      recipeNum = 0
    
    file = 'get_recipes/recipes/' + str(recipeNum/500) + '/' + str(recipeNum) + '.md'
    if recipeNum>startNum and os.path.isfile(file):
      logger.info(line)
      try:
        a = Recipe('get_recipes/recipes/' + str(recipeNum/500) + '/' + str(recipeNum) + '.md')
        recipe = a.returnJson()
        recipe['url'] = url
        recipe['title'] = title
        # Insert the new recipe
        try:
          recipeID = DB.newRecipe(recipe['title'],recipe['url'],recipe['source'],recipe['directions'],recipe['time'],recipe['total_cost'],recipe['total_cost_per_serving'],recipe['serving_size'],recipe['total_grams'],len(recipe['ingredients']))
        except:
          recipeID = DB.getRecipeIDfromURL(recipe['url'])
          
        # Update the nutrients
        for nutritionClass in recipe['nutrition'].keys():
          for nutrient in recipe['nutrition'][nutritionClass].keys(): 
            DB.updateIngredient(nutrient,recipe['nutrition'][nutritionClass][nutrient],recipeID)
        
        # Insert the ingredients
        for ingredient in recipe['ingredients']:
          try:
            actual = ingredient['actual']
            ingredient_uuid = recipe['url']+ingredient['ndb_no']
            measurement = ingredient['measurement']
            description = ingredient['description']
            ndb_no = ingredient['ndb_no']
            cost = ingredient['cost']
            grams = ingredient['grams']
            foo = DB.addIngredient(recipeID,ingredient_uuid,actual,measurement,description,ndb_no,cost,grams)
          except:
            logger.warning("ingredient already exists")
      except:
        logger.error("Unexpected error:", sys.exc_info()[0])
        
'''  
recipe = Recipe(sys.argv[1])
recipe['url']='asdlfkj'
try:
  recipeID = DB.newRecipe(recipe['title'],recipe['url'],recipe['source'],recipe['directions'],recipe['time'],recipe['total_cost'],recipe['total_cost_per_serving'],recipe['serving_size'],recipe['total_grams'],len(recipe['ingredients']))
except:
  recipeID = DB.getRecipeIDfromURL(recipe['url'])
for nutritionClass in recipe['nutrition'].keys():
  for nutrient in recipe['nutrition'][nutritionClass].keys(): 
    DB.updateIngredient(nutrient,recipe['nutrition'][nutritionClass][nutrient],recipeID)
for ingredient in recipe['ingredients']:
  print(ingredient)
  actual = ingredient['actual']
  ingredient_uuid = recipe['url']+ingredient['ndb_no']
  measurement = ingredient['measurement']
  description = ingredient['description']
  ndb_no = ingredient['ndb_no']
  cost = ingredient['cost']
  grams = ingredient['grams']
  foo = DB.addIngredient(recipeID,ingredient_uuid,actual,measurement,description,ndb_no,cost,grams)
break
'''
