The internet is full of recipes. A recipe is really only the *directions* and the *ingredients*, but for any given recipe website you always get a lot more information thatn you want (comments, links, advertisements). For instance the page for [Alton Brown's waffle](http://www.foodnetwork.com/recipes/alton-brown/basic-waffle-recipe.html) recipe looks like this:

![Website example](https://rpiai.files.wordpress.com/2015/02/webcontentgrabber-01.png)

How can you just pull out the directions and ingredients, in a tag-independent way that can be used across any website?

# Recipe extractor

## How it works

First it grabs the Markdown-formatted text of the html page using [html2text](https://github.com/aaronsw/html2text).  It evalutes the number of 'cooking' related words in each line and pulls out the peak.

![Website example](https://i.imgur.com/enu0SNA.jpg?1)

It does the same for extracting the ingredient list. Then it scans the directions and the ingredient list to determine what the *actual* baking time would be and gives that estimate. Finally, it parses the measurements and foods in the ingredient list and cross-references the USDA SR27 food databse to get accurate estimations of the nutrition content.

# To Do

- ~~Extract recipes.~~
- ~~Extract ingredients.~~
- ~~Cross references ingredients and measurements to USDA database.~~
- ~~Make AJAX interface.~~
- ~~Better identifying common foods in USDA database~~
- ~~Simpler conversion between food dimensions/weights~~
- ~~Add in pricing~~ 
- Clean up code by splitting into files
- Better error handling
- Add nice CSS into web interface.
- Add in photos of foods

## Installation

### Requirements

```
sudo apt-get install python-nltk
sudo pip install pint
```

Then goto python console
```python
>>> import nltk
>>> nltk.download('brown')
>>> nltk.download('maxent_treebank_pos_tagger')
>>> nltk.download('wordnet')
```

Clone the [SR27 database downloader](https://github.com/tscholl2/fudgen) and run the makefile to generate the database. Copy the database into the same folder. Then go into the database and make sqlite3 fts4 virtual table

```sql
drop table data;
drop table nutrition_date;
drop table nutrition_def;

create virtual table data using fts4(ndb_no,shrt_desc,long_desc,com_desc);
insert into data(ndb_no,shrt_desc,long_desc,com_desc) select ndb_no,shrt_desc,long_desc,com_desc from food_des;

create virtual table nutrition_data using fts4(ndb_no,nutr_no,nutr_val);
insert into nutrition_data(ndb_no,nutr_no,nutr_val) select ndb_no,nutr_no,nutr_val from nut_data;

create virtual table nutrition_def using fts4(nutr_no,units,tagname);
insert into nutrition_def(nutr_no,units,tagname) select nutr_no,units,tagname from nutr_def;
```




## Example

Visit the current incantation at http://ips.colab.duke.edu:8081/extractor.html and run which shows the extraction of the following recipe: [http://www.foodnetwork.com/recipes/alton-brown/baked-macaroni-and-cheese-recipe.html](http://www.foodnetwork.com/recipes/alton-brown/baked-macaroni-and-cheese-recipe.html).

Output:

```
# Baked Macaroni and Cheese

## Ingredients
------------------------------
- 1/2 pound elbow macaroni
- 0.5 pound MACARONI & CHS LOAF CHICK PORK & BF (19.0 g)

- 3 tablespoons butter
- 0.1875 cup BUTTER REPLCMNT,WO/FAT,PDR (15.0 g)

- 3 tablespoons flour
- 3.0 tablespoon WHEAT FLOURS,BREAD,UNENR (411.0 g)

- 1 tablespoon powdered mustard
- 1.0 tablespoon MUSTARD GRNS,FRZ,CKD,BLD,DRND,WO/SALT (150.0 g)

- 3 cups milk
- 3.0 cup MILK,GOAT,FLUID,W/ ADDED VITAMIN D (732.0 g)

- 1/2 cup yellow onion, finely diced
- 0.5 cup ONION RINGS,BREADED,PAR FR,FRZ,PREP,HTD IN OVEN (24.0 g)

- 1 bay leaf
- 1.0 dimensionless no match (1.0 g)

- 1/2 teaspoon paprika
- 0.5 teaspoon PAPRIKA (1.15 g)

- 1 large egg
- 1.0 dimensionless EGG,WHOLE,COOKED,OMELET (61.0 g)

- 12 ounces sharp cheddar, shredded
- 12.0 ounce SUNSHINE,CHEEZ-IT,DUOZ SHARP CHEDDAR PARMESAN CRACKERS (14.4 g)

- 1 teaspoon kosher salt
- 1.0 teaspoon SALT,TABLE (6.0 g)

- Fresh black pepper
- 0.0 dimensionless PEPPER,BLACK (0.0 g)

- Topping:
- 0.0 dimensionless no match (0.0 g)

- 3 tablespoons butter
- 3.0 tablespoon BUTTER,LT,STK,W/SALT (42.0 g)

- 1 cup panko bread crumbs
- 1.0 cup BREAD,SALVADORAN SWT CHS (QUESADILLA SALVADORENA) (55.0 g)

------------------------------

## Directions
Preheat oven to 350 degrees F.
In a large pot of boiling, salted water cook the pasta to al dente.
While the pasta is cooking, in a separate pot, melt the butter. Whisk in the
flour and mustard and keep it moving for about five minutes. Make sure it's
free of lumps. Stir in the milk, onion, bay leaf, and paprika. Simmer for ten
minutes and remove the bay leaf.
Temper in the egg. Stir in 3/4 of the cheese. Season with salt and pepper.
Fold the macaroni into the mix and pour into a 2-quart casserole dish. Top
with remaining cheese.
Melt the butter in a saute pan and toss the bread crumbs to coat. Top the
macaroni with the bread crumbs. Bake for 30 minutes. Remove from oven and rest
for five minutes before serving.
Remember to save leftovers for fried Macaroni and Cheese.
Recipe courtesy Alton Brown

+1 minutefor tossing.
# Calculated time: 51 minute


# Nutrition data (main)
Energy: 28416.864 kilojoule
Protein: 90.93 gram
Total lipid (fat): 161.34 gram
Carbohydrate, by difference: 441.43 gram
Sugars, total: 53.17 gram
Fiber, total dietary: 70.6 gram
Cholesterol: 539.0 milligram


# Nutrition data (ALL)
10:0: 1.802 gram
12:0: 1.942 gram
13:0: 0.0 gram
14:0: 6.655 gram
14:1: 0.036 gram
15:0: 0.032 gram
15:1: 0.0 gram
16:0: 27.568 gram
16:1 c: 0.106 gram
16:1 t: 0.009 gram
16:1 undifferentiated: 2.486 gram
17:0: 0.062 gram
17:1: 0.03 gram
18:0: 12.642 gram
18:1 c: 9.764 gram
18:1 t: 1.878 gram
18:1 undifferentiated: 38.272 gram
18:2 CLAs: 0.024 gram
18:2 n-6 c,c: 9.985 gram
18:2 t not further defined: 0.191 gram
18:2 undifferentiated: 24.091 gram
18:3 n-3 c,c,c (ALA): 1.883 gram
18:3 n-6 c,c,c: 0.084 gram
18:3 undifferentiated: 3.168 gram
18:3i: 0.0 gram
18:4: 0.0 gram
20:0: 0.147 gram
20:1: 0.298 gram
20:2 n-6 c,c: 0.025 gram
20:3 n-3: 0.0 gram
20:3 n-6: 0.006 gram
20:3 undifferentiated: 0.178 gram
20:4 undifferentiated: 0.246 gram
20:5 n-3 (EPA): 0.001 gram
22:0: 0.138 gram
22:1 c: 0.0 gram
22:1 t: 0.002 gram
22:1 undifferentiated: 0.073 gram
22:4: 0.016 gram
22:5 n-3 (DPA): 0.012 gram
22:6 n-3 (DHA): 0.066 gram
24:0: 0.034 gram
24:1 c: 0.0 gram
4:0: 2.11 gram
6:0: 1.211 gram
8:0: 0.86 gram
Alanine: 3.406 gram
Alcohol, ethyl: 0.0 gram
Arginine: 3.802 gram
Ash: 126.77 gram
Aspartic acid: 7.786 gram
Betaine: 52.8 milligram
Caffeine: 0.0 milligram
Calcium, Ca: 1380.0 milligram
Carbohydrate, by difference: 441.43 gram
Carotene, alpha: 607.0 microgram
Carotene, beta: 30942.0 microgram
Cholesterol: 539.0 milligram
Choline, total: 397.6 milligram
Copper, Cu: 2.635 milligram
Cryptoxanthin, beta: 6220.0 microgram
Cystine: 1.292 gram
Dihydrophylloquinone: 0.1 microgram
Energy: 28416.864 kilojoule
Fatty acids, total monounsaturated: 48.45 gram
Fatty acids, total polyunsaturated: 40.12 gram
Fatty acids, total saturated: 62.848 gram
Fatty acids, total trans: 3.169 gram
Fatty acids, total trans-monoenoic: 1.889 gram
Fatty acids, total trans-polyenoic: 0.191 gram
Fiber, total dietary: 70.6 gram
Fluoride, F: 57.4 microgram
Folate, DFE: 324.0 microgram
Folate, food: 267.0 microgram
Folate, total: 430.0 microgram
Folic acid: 34.0 microgram
Fructose: 8.2 gram
Galactose: 0.34 gram
Glucose (dextrose): 4.49 gram
Glutamic acid: 15.363 gram
Glycine: 2.95 gram
Histidine: 1.635 gram
Hydroxyproline: 0.0 gram
Iron, Fe: 45.25 milligram
Isoleucine: 3.29 gram
Lactose: 0.7 gram
Leucine: 5.963 gram
Lutein + zeaxanthin: 26613.0 microgram
Lycopene: 20.0 microgram
Lysine: 3.698 gram
Magnesium, Mg: 489.0 milligram
Maltose: 0.89 gram
Manganese, Mn: 16.436 milligram
Methionine: 1.553 gram
Niacin: 22.711 milligram
Pantothenic acid: 7.484 milligram
Phenylalanine: 3.544 gram
Phosphorus, P: 1424.0 milligram
Phytosterols: 277.0 milligram
Potassium, K: 5145.0 milligram
Proline: 8.11 gram
Protein: 90.93 gram
Retinol: 816.0 microgram
Riboflavin: 2.912 milligram
Selenium, Se: 121.7 microgram
Serine: 3.808 gram
Sodium, Na: 42477.0 milligram
Starch: 41.58 gram
Sucrose: 26.69 gram
Sugars, total: 53.17 gram
Theobromine: 0.0 milligram
Thiamin: 1.662 milligram
Threonine: 2.548 gram
Tocopherol, beta: 0.88 milligram
Tocopherol, delta: 5.92 milligram
Tocopherol, gamma: 21.74 milligram
Tocotrienol, alpha: 4.87 milligram
Tocotrienol, beta: 0.15 milligram
Tocotrienol, delta: 0.0 milligram
Tocotrienol, gamma: 0.14 milligram
Total lipid (fat): 161.34 gram
Tryptophan: 0.76 gram
Tyrosine: 2.677 gram
Valine: 4.086 gram
Vitamin A, IU: 59976.0 dimensionless
Vitamin A, RAE: 3679.0 microgram
Vitamin B-12: 1.99 microgram
Vitamin B-12, added: 0.0 microgram
Vitamin B-6: 3.262 milligram
Vitamin C, total ascorbic acid: 34.3 milligram
Vitamin D: 174.0 dimensionless
Vitamin D (D2 + D3): 4.3 microgram
Vitamin D3 (cholecalciferol): 4.0 microgram
Vitamin E (alpha-tocopherol): 36.25 milligram
Vitamin E, added: 0.0 milligram
Vitamin K (phylloquinone): 634.3 microgram
Water: 473.1 gram
Zinc, Zn: 11.05 milligram
```
