import numpy as np
import time
import random
import sys
import json

import string
keep = string.lowercase + string.digits + string.whitespace
table = string.maketrans(keep, keep)
delete = ''.join(set(string.printable) - set(keep))

import urllib2
from nltk.corpus import wordnet
from pattern.en import singularize, pluralize

from pint import UnitRegistry
ureg = UnitRegistry()

import sqlite3 as lite
con = lite.connect('db')

from fractions import Fraction
from os import listdir
from os.path import isfile, join
from unidecode import unidecode
import operator
from collections import OrderedDict
import markdown
from context_extractor import *

nutrientCategory = {}

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)
  
  
def getMixedFraction(flt):
  while True:
    fractionString = str(Fraction(flt).limit_denominator(8))
    if '/' in fractionString:
      fractionNums = str(Fraction(flt).limit_denominator(8)).split('/')
      num = int(fractionNums[0])
      if '8' in fractionNums[1] or '4' in fractionNums[1] or '3' in fractionNums[1]:
        den = int(fractionNums[1])
        if num<den:
          return str(num) + "/" + str(den)
        else:
          return str(num/den) + " " + str(num-den*(num/den)) + "/" + str(den)
      else:
        flt = flt - 0.05
    else:
      return str(round(flt))
      

class Recipe:
  def __init__(self,source,title='None'):
    contexts = json.load(open('context_settings.json','r'))
    (o_snippet,o_fits,o_array) = get_snippets(contexts,source)
    self.nutrients = {}
    self.recipe = {}
    self.htmlString = ""
    if 'None' in title:
      self.title = o_snippet['title']
    self.directions = o_snippet['directions'].replace('> ','').replace('>','')
    self.ingredients = []
    for line in o_snippet['ingredients'].split('\n'):
      if len(line)>4:
        self.ingredients.append(self.parseIngredients(line.replace('> ','').replace('>','')))
    self.recipe['title'] = self.title
    self.recipe['source'] = source
    self.recipe['ingredients'] = self.ingredients
    self.recipe['nutrition'] = self.nutrients
    self.recipe['directions'] = self.directions
    self.recipe['time'] = self.extractCookingTime(self.directions)
    self.recipe['total_cost'] = 0
    for ingredient in self.recipe['ingredients']:
      self.recipe['total_cost'] = self.recipe['total_cost'] + ingredient['cost']
    self.recipe['total_grams'] = 0
    for ingredient in self.recipe['ingredients']:
      self.recipe['total_grams'] = self.recipe['total_grams'] + ingredient['grams']
    self.recipe['serving_size'] = round(self.recipe['nutrition']['Main']['Energy']/600,1)
    for nutrientType in self.recipe['nutrition']:
      for item in self.recipe['nutrition'][nutrientType]:
        self.recipe['nutrition'][nutrientType][item] = self.recipe['nutrition'][nutrientType][item]/self.recipe['total_grams']*100
    self.recipe['total_cost'] = round(self.recipe['total_cost'],2)
    self.recipe['total_cost_per_serving'] = round(self.recipe['total_cost']/self.recipe['serving_size'],2)
    self.recipe['url']=source
    #print json.dumps(self.recipe['ingredients'],sort_keys=True,indent=2)
    #print json.dumps(self.recipe['directions'],sort_keys=True,indent=2)
#    print(json.dumps(self.recipe,sort_keys=True,indent=2))
#    with open('collected_recipes.json','a') as f:
#      f.write(json.dumps(self.recipe) + "\n")
    
    
  def returnJson(self):
    return self.recipe

    
  def parseIngredients(self,sentence):
    # Baseline construct
    ingredient = {'actual':sentence.replace('*','').replace('-','').strip(),'measurement':'No measurement match','description':'No food match','grams':0,'cost':0,'ndb_no':'None'}
    # Remove things in parentheses
    regEx = re.compile(r'([^\(]*)\([^\)]*\) *(.*)')
    m = regEx.match(sentence)
    while m:
      sentence = m.group(1) + m.group(2)
      m = regEx.match(sentence)

    sentence = sentence.lower()
    sentence = sentence.replace('about pound','1 pound')
    sentence = sentence.replace('-',' ')
    sentence = sentence.replace(' or ',' ')
    sentence = sentence.replace(' and ',' ')
    sentence = sentence.replace(' to ',' ')
    sentence = sentence.replace(' for ',' ')
    sentence = sentence.replace('white sugar','granulated sugar')
    sentence = sentence.replace('(','')
    sentence = sentence.replace(')','')
    sentence = sentence.replace('about','')
    sentence = sentence.replace('handful','cup')
    sentence = sentence.replace('and/or','')
    sentence = sentence.replace('11/2','1 1/2')
    sentence = sentence.replace('11/8','1 1/8')
    sentence = sentence.replace('11/4','1 1/4')
    sentence = sentence.replace('13/4','1 3/4')
    sentence = sentence.replace('21/2','2 1/2')
    sentence = sentence.replace('21/8','2 1/8')
    sentence = sentence.replace('21/4','2 1/4')
    sentence = sentence.replace('23/4','2 3/4')
    sentence = sentence.replace('31/2','3 1/2')
    sentence = sentence.replace('31/8','3 1/8')
    sentence = sentence.replace('31/4','3 1/4')
    sentence = sentence.replace('33/4','3 3/4')
    sentence = sentence.replace(' / ',' ')
    sentence = sentence.replace(' / ',' ')
    sentenceFoo = sentence
    for word in sentenceFoo.split():
      if len(word)>5 and '/' in word:
        sentence = sentence.replace(word,' '.join(word.split('/')))
    sentence = sentence.replace('/','slashslash')
    # Remove punctuation

    exclude = set(string.punctuation)
    sentence = ''.join(ch for ch in sentence if ch not in exclude)
    sentence = sentence.replace('slashslash','/')
    words = sentence.split()
    # Sanitize the words
    for i in range(len(words)):
      if words[i][-1] == 's':
        words[i] = singularize(words[i])
      if '/' in words[i]:
        try:
          words[i]=str(ureg.parse_expression(words[i]).magnitude)
        except:
          words[i]=str(ureg.parse_expression(words[i]))
    
    # Determine which words are ingredients and which are measurements (quantities)
    foodWords = [False]*len(words)
    measurementWords = [False]*len(words)
    quantityExpression = "none"
    for i in range(len(words)):
      synsets = wordnet.synsets(words[i])
      try:
        foo = ureg.parse_expression(words[i])
        measurementWords[i] = True
      except:
        pass
        
      for synset in synsets:
        if "none" in quantityExpression and hasNumbers(words[i]):
          quantityExpression = words[i] + ' dimensionless'
        if i>0 and 'quantity' in synset.lexname and hasNumbers(words[i-1]):
          quantityExpression = words[i-1] + " " + words[i]
          measurementWords[i] = True
          measurementWords[i-1] = True
        if 'food' in synset.lexname or 'plant' in synset.lexname:
          if not measurementWords[i]:
            foodWords[i] = True
        if i>1 and 'quantity' in synset.lexname and hasNumbers(words[i-1]) and hasNumbers(words[i-2]):
          quantityExpression = str(float(words[i-2]) + float(words[i-1])) + " " + words[i]
          measurementWords[i] = True
          measurementWords[i-1] = True
          measurementWords[i-2] = True

    # Figure out the grams
    tryToFindAnotherMeasure = False
    try:
      foodGrams = ureg.parse_expression(quantityExpression).to(ureg.grams)
    except:
      try:
        mills = ureg.parse_expression(quantityExpression).to(ureg.milliliters)
        foodGrams = mills.magnitude*ureg.grams
        tryToFindAnotherMeasure = True
      except:
        try:
          foodGrams = float(quantityExpression[0])*ureg.dimensionless
        except:
          foodGrams = 1*ureg.dimensionless

    
    # Generate some food search strings using the food words and the words around the food words
    possibleWords = []
    # Fixes
    if "baking" in words and "powder" in words:
      possibleWords.append('baking* NEAR/3 powder*')
    if "baking" in words and "soda" in words:
      possibleWords.append('sodium* NEAR/3 bicarbonate*')
    if "vinegar" in words:
      possibleWords.append('vinegar*')
    if "asparagu" in words:
      possibleWords.append('asparagus')
    for i in range(len(words)):
      if i>0 and foodWords[i]:
        if not measurementWords[i-1]:
          possibleWords.append(words[i-1] + '* NEAR/3 ' + words[i] + '*')
      if i<len(foodWords)-1 and foodWords[i]:
        if not measurementWords[i+1]:
          possibleWords.append(words[i] + '* NEAR/3 ' + words[i+1] + '*')
    for i in range(len(foodWords)):
      if foodWords[i]:
        possibleWords.append(words[i] + '*')
    # More fixes
    if "chocolate" in words and "chip" in words:
      possibleWords = []
      possibleWords.append('Candies, semisweet chocolate')
    if "flour" in words and "tortilla" in words:
      possibleWords = []
      possibleWords.append('tortillas NEAR/5 flour')
    if "berries" in sentence or "strawberries" in sentence:
      possibleWords = []
      possibleWords.append('strawberries')
    if "blueberries" in sentence:
      possibleWords = []
      possibleWords.append('strawberries')
    if "yogurt cream" in sentence:
      possibleWords = []
      possibleWords.append('yogurt NEAR/3 cream')
    if "can" in sentence and "pumpkin" in sentence:
      possibleWords = []
      possibleWords.append('pumpkin NEAR/3 canned')
    if "olives" in sentence:
      possibleWords = []
      possibleWords.append('olives NEAR/3 canned')
    # Start searching the db
    foundMatch = False
    shrt_desc = "No match"
    ndb_no = '-1'
    with con:
      cur = con.cursor()    
      for possibleWord in possibleWords:
        if not foundMatch:
          cur.execute('select ndb_no,long_desc,com_desc,length(com_desc)-length("'+possibleWord.replace('*','').split()[0] + '") as closest from data where com_desc match "' + possibleWord.replace('*','') + '" order by closest')

          row = cur.fetchone()
          if row is not None:
            ndb_no =  row[0].encode('utf-8')
            shrt_desc = row[1].encode('utf-8')
            com_desc = row[2].encode('utf-8')
            foundMatch = True
            break
      # search the google hits simultaneously   
      if not foundMatch:
        for possibleWord in possibleWords:
          cur.execute('select c.ndb_no,shrt_desc,google_hits,length(long_desc)-length("'+possibleWord.replace('*','').split()[0] + '") as closest from ranking as r join data as c on r.ndb_no=c.ndb_no where long_desc match "'+possibleWord+'" order by google_hits desc')

          row = cur.fetchone()
          if row is not None:
            ndb_no =  row[0].encode('utf-8')
            shrt_desc = row[1].encode('utf-8')
            foundMatch = True
            break

      if foundMatch:
        cur.execute('select price from food_des where ndb_no like "'+ndb_no+'"')
        row = cur.fetchone()
        try:
          price =  float(row[0])
        except:
          price = 0

    if not foundMatch:
      return ingredient
    
    # Now that you have the food but not a good measurement (cups, etc.) try to match one in the table
    if tryToFindAnotherMeasure:
      with con:
        cur.execute('select ndb_no,amount,msre_desc,gm_wgt from weight where ndb_no like "'+ndb_no+'"')
        rows = cur.fetchall()
        for row in rows:
          try:
            if ureg.parse_expression(quantityExpression).dimensionality == ureg.parse_expression(row[2]).dimensionality:
              foo = ureg.parse_expression(quantityExpression).to(ureg.parse_expression(row[2]))
              foodGrams = foo.magnitude * row[3] * ureg.grams
              break
          except:
            pass
    # Get an appropriate measurement from weights table, or if there is no grams assigned, pick something from the weights table
    measurementString = "1 dimensionless"
    measurementAmount = 1
    with con:
      cur.execute('select ndb_no,amount,msre_desc,gm_wgt,abs(gm_wgt-'+str(foodGrams.magnitude)+') as diff from weight where ndb_no like "'+ndb_no+'" order by diff')
      row = cur.fetchone()
      if row is not None and len(row)>3:    
        if str(foodGrams.dimensionality)=='dimensionless':
          measurementAmount = float(row[1]) * float(foodGrams.magnitude)
          foodGrams = (measurementAmount*float(row[3]))*ureg.grams
          measurementString = getMixedFraction(measurementAmount) + ' ' + row[2]
        else:
          measurementAmount = float(foodGrams.magnitude) / (float(row[1]) * float(row[3]))
          measurementString = getMixedFraction(measurementAmount)  + ' ' + row[2]

    
    # Get nutrition
    self.getNutrition(ndb_no,foodGrams.magnitude/100.0)
    ingredient['measurement']=measurementString
    ingredient['ndb_no']=ndb_no
    ingredient['grams']=foodGrams.magnitude
    ingredient['cost']=price*foodGrams.magnitude
    ingredient['description']=shrt_desc
    return ingredient

      
  def getNutrition(self,foodId,multiplier):
    with con:
        
      cur = con.cursor()    
      cur.execute('select nutr_no,nutr_val from nutrition_data where ndb_no match "'+foodId+'"')
      rows = cur.fetchall()

      for row in rows:
        id = int(row[0])
        nutr_val = float(row[1])*multiplier
        if nutr_val > 0:
          cur2 = con.cursor() 
          cur2.execute('select units,NutrDesc,sr_order from nutr_def where nutr_no == "'+str(id)+'" order by sr_order')
          rows2 = cur2.fetchone()
          units = rows2[0]
          name = rows2[1]
          newUnits = ureg.dimensionless
          useMagnitudeOnly = False
          try:
            if '[length] ** 2 * [mass] / [time] ** 2' == str(ureg.parse_expression(units).dimensionality):
              newUnits = ureg.kilocalorie
            elif '[mass]' == str(ureg.parse_expression(units).dimensionality):
              newUnits = ureg.grams
          except:
            useMagnitudeOnly = True
            
          if name not in nutrientCategory: 
            c = int(rows2[2])
            if c < 1600:
              nutrientCategory[name] = 'Main'
            elif c < 5300:
              nutrientCategory[name] = 'Sugars'
            elif c < 6300:
              nutrientCategory[name] = 'Metals'
            elif c < 9700:
              nutrientCategory[name] = 'Vitamins'
            elif c < 15700:
              nutrientCategory[name] = 'Fatty Acids'
            elif c < 16300:
              nutrientCategory[name] = 'Steroids'
            elif c < 18200:
              nutrientCategory[name] = 'Amino acids'
            elif c < 18500:
              nutrientCategory[name] = 'Other'
          if nutrientCategory[name] not in self.nutrients:
            self.nutrients[nutrientCategory[name]] = {}
            self.nutrients[nutrientCategory[name]][name.encode('utf-8')] = 0
          if name.encode('utf-8') not in self.nutrients[nutrientCategory[name]]:
            self.nutrients[nutrientCategory[name]][name.encode('utf-8')] = 0
          if useMagnitudeOnly:
            additionalValue = nutr_val
          else:
            additionalValue = (nutr_val * ureg.parse_expression(units)).to(newUnits).magnitude
          self.nutrients[nutrientCategory[name]][name.encode('utf-8')]=self.nutrients[nutrientCategory[name]][name.encode('utf-8')] + additionalValue
          
          
  def extractCookingTime(self,directions):
    data = directions.lower()
    data = data.replace('\n',' ')
    data = data.replace('one','1')
    data = data.replace('two','2')
    data = data.replace('three','3')
    data = data.replace('four','4')
    data = data.replace('five','5')
    data = data.replace('six','6')
    data = data.replace('seven','7')
    data = data.replace('eight','8')
    data = data.replace('nine','9')
    data = data.replace('ten','10')
    data = data.replace('twenty','20')
    data = data.replace('thirty','30')
    data = data.replace('forty','40')
    data = data.replace('fifty','50')
    data = data.replace('sixty','60')
    data = data.replace('overnight','12 hours')
    data = data.replace('few minute','3 minute')
    data = data.replace('few hour','3 hour')
    data = data.replace('another minute','1 minute')
    data = data.replace('several minute','4 minute')
    data = data.replace('one more minute','1 minute')
    data = data.replace('cook until','2 minute')
    data = data.replace('-',' ')
    exclude = set(string.punctuation)
    data = ''.join(ch for ch in data if ch not in exclude)


    dataWords =  data.split()
    timeWords = ['minute','minutes','hour','hours']
    totalTime = 0*ureg.minute
    for timeWord in timeWords:
      timeI = [i for i, x in enumerate(dataWords) if x == timeWord]
      for i in timeI:
        try:
          totalTime = totalTime + int(dataWords[i-1])*ureg.parse_expression(dataWords[i])
        except:
          pass

    dataWords =  data.split()
    cookingTimes = {'cut':1*ureg.minute,'knead':2*ureg.minute,'chop':1*ureg.minute,'food processor':2*ureg.minute,'slice':1*ureg.minute,'assemble':1*ureg.minute,'toss':1*ureg.minute,'filet':1*ureg.minute,'stuff':1*ureg.minute}
    for key in cookingTimes.keys():
      timesInData = [i for i, x in enumerate(dataWords) if x == key]
      totalTime = totalTime + len(timesInData)*cookingTimes[key]
      if len(timesInData)>0:
        print("+"+ len(timesInData)*str(cookingTimes[key]) + " for " + key + "ing.\n")
      
    if totalTime > 60*ureg.minute:
      return str(totalTime.to(ureg.hour))
    else:
      return str(totalTime)

    

    
  def extract_recipe_main(url):
    global nutrientData
    nutrientData = OrderedDict()
    totalPrice = 0
    finalString = ''
    titleString = ''
    
    mypath = 'get_google_images/images/'
    onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
    snippets = get_snippets(contexts,url) 
    data_ingredients = snippets['ingredients']  
    data = snippets['directions']
    exclude = set(string.punctuation)
    #print '# ' + json_data['name'] + "\n"
    imageGridUrls = []
    finalString = finalString + '# ' + titleString + '\n\n'
    finalString = finalString + '# Ingredients\n\n' 
    nutrition  = {}
    start = time.time()
    for line in data_ingredients.split('\n'):
      if len(line)>2:
        finalString = finalString + ' - ' + line.strip().replace('-','').replace('*','') + '\n'
        (food,foodId,measurement,grams,nutrition,price) = getFoodFromDatabase(line,nutrition)
        totalPrice = totalPrice + price
        finalString = finalString + " - "
        imageName = None
        for i in onlyfiles:
          if foodId in i:
            imageName = i
            break
        if imageName is not None:
          finalString = finalString + "<img src='http://ips.colab.duke.edu/extract_recipe/get_google_images/images/" + imageName + "' width=50>"
          imageGridUrls.append("<img src='http://ips.colab.duke.edu/extract_recipe/get_google_images/images/" + imageName + "' width=30>")
        finalString = finalString + ' - ' + str(measurement) + " " 
        try:
          finalString = finalString + food + " (" + str(round(grams.magnitude,1)) + " grams)" + " - $" + str(round(price,2)) + "\n"
        except:
          pass
    end = time.time()
    print(end-start)

    finalString = finalString + "\n"
    patternString = '<section id="photos">\n'
    for i in imageGridUrls:
      patternString = patternString + i + '\n'
    patternString = patternString + "</section>\n" 
    print(patternString)
    
    finalString = patternString + "\n" + finalString
   
    '''
    ingredients = ''
    for ingredient in json_data['ingredients'].split('\n'):
      print " - " + ''.join(ch for ch in ingredient if ch not in exclude)
      ingredients = ingredients + ' ' + ''.join(ch for ch in ingredient if ch not in exclude)
    '''
    finalString = finalString + "\n"
    finalString = finalString + '# Directions\n' 

    finalString = finalString + data
    finalString = finalString + "\n"
    data = data.lower()
    data = data.replace('\n',' ')
    data = data.replace('one','1')
    data = data.replace('two','2')
    data = data.replace('three','3')
    data = data.replace('four','4')
    data = data.replace('five','5')
    data = data.replace('six','6')
    data = data.replace('seven','7')
    data = data.replace('eight','8')
    data = data.replace('nine','9')
    data = data.replace('ten','10')
    data = data.replace('twenty','20')
    data = data.replace('thirty','30')
    data = data.replace('forty','40')
    data = data.replace('fifty','50')
    data = data.replace('sixty','60')
    data = data.replace('overnight','12 hours')
    data = data.replace('few minute','3 minute')
    data = data.replace('few hour','3 hour')
    data = data.replace('another minute','1 minute')
    data = data.replace('several minute','4 minute')
    data = data.replace('one more minute','1 minute')
    data = data.replace('cook until','2 minute')
    data = data.replace('-',' ')
    data = ''.join(ch for ch in data if ch not in exclude)


    dataWords =  data.split()
    timeWords = ['second','seconds','minute','minutes','hour','hours']
    totalTime = 0*ureg.minute
    for timeWord in timeWords:
      timeI = [i for i, x in enumerate(dataWords) if x == timeWord]
      for i in timeI:
        try:
          totalTime = totalTime + int(dataWords[i-1])*ureg.parse_expression(dataWords[i])
        except:
          pass

    data = data + ' ' + data_ingredients
    dataWords =  data.split()
    cookingTimes = {'cut':1*ureg.minute,'boil':6*ureg.minute,'knead':2*ureg.minute,'chop':1*ureg.minute,'food processor':2*ureg.minute,'slice':1*ureg.minute,'assemble':1*ureg.minute,'toss':1*ureg.minute,'filet':1*ureg.minute,'stuff':1*ureg.minute}
    for key in cookingTimes.keys():
      timesInData = [i for i, x in enumerate(dataWords) if x == key]
      totalTime = totalTime + len(timesInData)*cookingTimes[key]
      if len(timesInData)>0:
        finalString = finalString + "+"
        finalString = finalString + len(timesInData)*str(cookingTimes[key])
        finalString = finalString + " for " + key + "ing."
        finalString = finalString + "\n"
      
    if totalTime > 60*ureg.minute:
      finalString = finalString + "# Calculated time: "
      finalString = finalString + str(totalTime.to(ureg.hour))
      finalString = finalString + "\n"
    else:
      finalString = finalString + "# Calculated time: "
      finalString = finalString + str(totalTime)
      finalString = finalString + "\n"
    
    finalString = finalString + "# Calculated cost: $"
    finalString = finalString + "%.2f"%totalPrice
    finalString = finalString + "\n"

    nutrition['Energy'] = str(ureg.parse_expression(nutrition['Energy']).to(ureg.kilocalorie))
    nutMag = {}
    for i in nutrition:
      try:
        nutMag[i] = ureg.parse_expression(nutrition[i]).to(ureg.grams).magnitude
      except:
        nutMag[i] = ureg.parse_expression(nutrition[i]).magnitude/1000 

    sorted_nut = sorted(nutrientCategoryNum.items(), key=operator.itemgetter(1),reverse=False)

    
    servings = round(nutrientData['Main']['Energy']/650)
    
    finalString = finalString +  "\n\n# Serving size is about " + str(servings) + "\n"
    '''
    finalString = finalString + "\n\n# Nutrition data (main)\n"
    importantNutrition = ['Energy','Protein','Total lipid (fat)','Carbohydrate, by difference','Sugars, total','Fiber, total dietary','Cholesterol']
    for key in importantNutrition:
      finalString = finalString +  key + ": " + nutrition[key]  + "\n"
    print "\n\n"
    '''  
    '''
    finalString = finalString + "\n\n# Nutrition data (ALL)\n"
    lastCategory = "None"
    for i in sorted_nut:
      key = i[0]
      category = nutrientCategory[key]
      if lastCategory is not category:
        finalString = finalString + "\n## "  + category + "\n"
        lastCategory = category
      finalString = finalString +  key + ": " + nutrition[key]  + "\n"
    '''
    
    finalString = finalString + "\n\n# Nutrition data (ALL)\n"
    for category in nutrientData:
      finalString = finalString + "\n\n## " + category + "\n\n"
      print(category)
      print(nutrientData[category])
      for nutrient in sorted(nutrientData[category].items(), key=operator.itemgetter(1),reverse=True):
        if nutrient[1]>0:
          if 'Energy' in nutrient[0]:
            finalString = finalString + " - " + nutrient[0] + ": " + str(nutrient[1]) + " Calories\n"
          elif "IU" in nutrient[0]:
            finalString = finalString + " - " + nutrient[0] + ": " + str(nutrient[1]) + " IU\n"
          else:
            finalString = finalString + " - " + nutrient[0] + ": " + str(nutrient[1]) + " grams\n"
        
    return markdown.markdown(unidecode(finalString))

#print extract_recipe_main('http://www.marthastewart.com/344840/soft-and-chewy-chocolate-chip-cookies')
#print extract_recipe_main('http://www.foodnetwork.com/recipes/alton-brown/baked-macaroni-and-cheese-recipe.html')
#print extract_recipe_main('http://www.foodnetwork.com/recipes/alton-brown/southern-biscuits-recipe.html')
#extract_recipe_main(sys.argv[1])


'''

Useful SQLITE commands

List nutrients
select nutr_no,nutrdesc from nutr_def order by sr_order;


FInd top 50 foods for a given nutrient:
select long_desc,nutr_no,nutr_val from (select long_desc,nutr_no,nutr_val from food_des,nut_data where food_des.ndb_no == nut_data.ndb_no) where nutr_no like '328' order by nutr_val desc limit 50;
'''
#a = Recipe(sys.argv[1])
