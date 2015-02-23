'''
This program the Amazon results for each food to determine the prices
'''

from pint import UnitRegistry
ureg = UnitRegistry()
# Need to define fluid ounces
ureg.define('fl = 29.5735 * milliliter')
import numpy as np
import pprint
import operator
import os, fnmatch

def reject_outliers(points, thresh=3.5):
  """
  Returns a boolean array with True if points are outliers and False 
  otherwise.

  Parameters:
  -----------
      points : An numobservations by numdimensions array of observations
      thresh : The modified z-score to use as a threshold. Observations with
          a modified z-score (based on the median absolute deviation) greater
          than this value will be classified as outliers.

  Returns:
  --------
      mask : A numobservations-length boolean array.

  References:
  ----------
      Boris Iglewicz and David Hoaglin (1993), "Volume 16: How to Detect and
      Handle Outliers", The ASQC Basic References in Quality Control:
      Statistical Techniques, Edward F. Mykytka, Ph.D., Editor. 
  """
  if len(points.shape) == 1:
    points = points[:,None]
  median = np.median(points, axis=0)
  diff = np.sum((points - median)**2, axis=-1)
  diff = np.sqrt(diff)
  med_abs_deviation = np.median(diff)

  modified_z_score = 0.6745 * diff / med_abs_deviation

  isOutlier = modified_z_score > thresh
  newArray = np.array([])
  for i in range(0,points.size):
    if not isOutlier[i]:
      newArray = np.append(newArray,points[i])
  return newArray
    
def findFiles (path, filter):
    for root, dirs, files in os.walk(path):
        for file in fnmatch.filter(files, filter):
            yield os.path.join(root, file)
            
    
def hasNumbers(inputString):
  return any(char.isdigit() for char in inputString)

def ispunct(some_string):
    return not any(char.isalnum() for char in some_string)
    
def extractUnits(title):
  unitExpression = None
  multiplier = 1
  title = title.lower()
  title = title.replace('-',' ')
  title = title.replace('0g','0 grams ')
  title = title.replace('$',' ')
  title = title.replace('ct',' count ')
  title = title.replace('%',' ')
  title = title.replace(')',' ')
  title = title.replace('(',' ')
  title = title.replace('[',' ')
  title = title.replace(']',' ')
  title = title.replace(',',' ')
  title = title.replace('"',' ')
  title = title.replace('/',' ')
  title = title.replace('_',' ')
  title = title.replace(':',' ')
  title = title.replace('+',' ')
  title = title.replace('#',' ')
  title = title.replace('\'',' ')
  
  newString = ""
  lastWasAlpha = False
  lastWasDigit = False
  for i in title:
    if lastWasDigit and i.isalpha():
      newString = newString + " "  
    if lastWasAlpha and i.isdigit():
      newString = newString + " "
    if lastWasAlpha and ispunct(i):
      newString = newString + " "
    lastWasAlpha = i.isalpha()
    lastWasDigit = i.isdigit()
    newString = newString + i
  title = newString
  words = title.lower().split()
  #print words
  numIndicies = []
  for i in range(len(words)):
    #print words[i]
    if hasNumbers(words[i]):
      words[i]=str(ureg.parse_expression(words[i]))
      numIndicies.append(i)
      if i>1:
        if 'of' == words[i-1]:
          if 'pack' == words[i-2] or 'count' == words[i-2]:
            multiplier = int(words[i])
        if 'pack' == words[i-1]:
          multiplier = int(words[i])
      if i+1<len(words):
        if 'per' == words[i+1] or 'pack' == words[i+1] or 'count' == words[i+1]:
          multiplier = int(words[i])
    else:
      words[i] = words[i].replace(',','')
      words[i] = words[i].replace('.','')
      
  for i in range(len(words)):
    try:
      if hasNumbers(words[i]):
        unitExpression = ureg.parse_expression(words[i] + ' ' + words[i+1])
    except:
      pass
  return (unitExpression,multiplier)

  
  
  
#print extractUnits(' Simply Organic Pumpkin Pie Spice, Mini Spice, 0.46 Ounce (Pack of 6)')  
  

for textFile in findFiles(r'ndb_nos', '*.txt'):
  ndb_no = textFile.split('/')[1].split('.')[0]
  units = {}
  prices = []
  with open(textFile,'rb') as f:
    for line in f:
      try:
        (num,price,title) = line.split('\t')
        price = float(price)
        (extractedWeight,multiplier) = extractUnits(title)
        unitType = str((1/extractedWeight).dimensionality)
      except:
        unitType = None
      if unitType is not None:
        if unitType in units:
          units[unitType] = units[unitType] + 1
        else:
          units[unitType] = 1
        pricePerProduct = (price/extractedWeight)/multiplier
        prices.append(pricePerProduct)
        '''
        try:
          print str(price) + '\t' + str(extractedWeight) + '\t' + str(multiplier)  + '\t' + str(pricePerProduct.to(1 / ureg.gram)) + '\t' + title
        except:
          pass
        '''


  sorted_units = sorted(units.items(), key=operator.itemgetter(1),reverse=True)
  commonDimensionality = None
  for unit in sorted_units:
    commonDimensionality = unit[0]
    break

  units = {}
  for price in prices:
    unitType = str(price.units)
    if commonDimensionality == price.dimensionality:
      if unitType in units:
        units[unitType] = units[unitType] + 1
      else:
        units[unitType] = 1
        
  sorted_units = sorted(units.items(), key=operator.itemgetter(1),reverse=True)
  for unit in sorted_units:
    commonUnit = unit[0]
    break

  pricePerDimension = np.array([])
  for price in prices:
    if commonDimensionality == price.dimensionality:
      try:
        if commonDimensionality == '1 / [mass]':
          commonUnit = str(1 / ureg.gram)
          convertedPrice =  price.to(1 / ureg.gram)
        else:
          commonUnit = str(1 / ureg.parse_expression('milliliter'))
          convertedPrice =  price.to(1 / ureg.parse_expression('milliliter'))
        pricePerDimension = np.append(pricePerDimension,convertedPrice.magnitude)
      except:
        pass
     
  np.set_printoptions(precision=4,linewidth=100000)
  delimiter = '^'
  if reject_outliers(pricePerDimension).size > 1:
    with open('ndb_mean_std_unit.txt','a') as f:
      f.write(ndb_no + delimiter + str(round(np.average(reject_outliers(pricePerDimension)),6)) + delimiter+ str(round(np.std(reject_outliers(pricePerDimension)),6)) + delimiter + str((1/ureg.parse_expression(commonUnit)).units) + '\n')
      #print(ndb_no + delimiter + str(round(np.average(reject_outliers(pricePerDimension)),6)) + delimiter+ str(round(np.std(reject_outliers(pricePerDimension)),6)) + delimiter + str((1/ureg.parse_expression(commonUnit)).units) + '\n')
