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

# Ingredients

  * 1/2 pound elbow macaroni
 - <img src='http://ips.colab.duke.edu/extract_recipe/get_google_images/images/20099.jpg' width=50>2 1/8 cup elbow shaped Macaroni, dry, enriched (226.8 grams) - $3.76

  * 3 tablespoons butter
 - <img src='http://ips.colab.duke.edu/extract_recipe/get_google_images/images/01001.jpg' width=50>3.0 tbsp Butter, salted (42.6 grams) - $1.08

  * 3 tablespoons flour
 - <img src='http://ips.colab.duke.edu/extract_recipe/get_google_images/images/20581.jpg' width=50>1/8 cup Wheat flour, white, all-purpose, enriched, unbleached (23.4 grams) - $0.12

  * 1 tablespoon powdered mustard
 - <img src='http://ips.colab.duke.edu/extract_recipe/get_google_images/images/02046.jpg' width=50>3 1/8 tsp or 1 packet Mustard, prepared, yellow (15.6 grams) - $0.41

  * 3 cups milk
 - <img src='http://ips.colab.duke.edu/extract_recipe/get_google_images/images/01077.jpg' width=50>3/4 quart Milk, whole, 3.25% milkfat, with added vitamin D (732.0 grams) - $0.58

  * 1/2 cup yellow onion, finely diced
 - <img src='http://ips.colab.duke.edu/extract_recipe/get_google_images/images/11282.jpg' width=50>1.0 cup, sliced Onions, raw (118.3 grams) - $3.93

  * 1 bay leaf
 - <img src='http://ips.colab.duke.edu/extract_recipe/get_google_images/images/02004.png' width=50>1.0 tsp, crumbled Spices, bay leaf (0.6 grams) - $0.09

  * 1/2 teaspoon paprika
 - <img src='http://ips.colab.duke.edu/extract_recipe/get_google_images/images/02028.jpg' width=50>1/3 tsp Spices, paprika (1.1 grams) - $0.07

  * 1 large egg
 - <img src='http://ips.colab.duke.edu/extract_recipe/get_google_images/images/01123.jpg' width=50>1.0 small Egg, whole, raw, fresh (38.0 grams) - $0.19

  * 12 ounces sharp cheddar, shredded
 - <img src='http://ips.colab.duke.edu/extract_recipe/get_google_images/images/01270.jpg' width=50>12 1/8 slice 1 oz. slice CHEESE,CHEDDAR,SHARP,SLICED (340.2 grams) - $10.3

  * 1 teaspoon kosher salt
 - <img src='http://ips.colab.duke.edu/extract_recipe/get_google_images/images/02047.jpg' width=50>1.0 tsp Salt, table (6.0 grams) - $0.19

  * Fresh black pepper
 - <img src='http://ips.colab.duke.edu/extract_recipe/get_google_images/images/02030.jpg' width=50>1.0 dash Spices, pepper, black (0.1 grams) - $0.0

  * Topping:
 - <img src='http://ips.colab.duke.edu/extract_recipe/get_google_images/images/21226.png' width=50>1.0 serving 5 servings per 22.85 oz package PIZZA,MEAT & VEG TOPPING,REG CRUST,FRZ,CKD (129.0 grams) - $0.0

  * 3 tablespoons butter
 - <img src='http://ips.colab.duke.edu/extract_recipe/get_google_images/images/01001.jpg' width=50>3.0 tbsp Butter, salted (42.6 grams) - $1.08

  * 1 cup panko bread crumbs
 - <img src='http://ips.colab.duke.edu/extract_recipe/get_google_images/images/18069.jpg' width=50>5 1/4 cup, crumbs Bread, white, commercially prepared (includes soft bread crumbs) (236.6 grams) - $2.83


# Directions
In a large pot of boiling, salted water cook the pasta to al dente.
While the pasta is cooking, in a separate pot, melt the butter. Whisk in the flour and mustard and keep it moving for about five minutes. Make sure it's free of lumps. Stir in the milk, onion, bay leaf, and paprika. Simmer for ten minutes and remove the bay leaf.
Temper in the egg. Stir in 3/4 of the cheese. Season with salt and pepper. Fold the macaroni into the mix and pour into a 2-quart casserole dish. Top with remaining cheese.
Melt the butter in a saute pan and toss the bread crumbs to coat. Top the macaroni with the bread crumbs. Bake for 30 minutes. Remove from oven and rest for five minutes before serving.
Remember to save leftovers for fried Macaroni and Cheese.
Recipe courtesy Alton Brown

+1 minute for tossing.
# Calculated time: 51 minute
# Calculated cost: $24.64


# Serving size is about 13.0


# Nutrition data (ALL)


## Main

 - Energy: 8542.51051625 Calories
 - Water: 539.29 grams
 - Carbohydrate, by difference: 441.39 grams
 - Total lipid (fat): 257.0 grams
 - Ash: 134.75 grams
 - Protein: 122.14 grams
 - Fiber, total dietary: 103.0 grams
 - Sugars, total: 35.41 grams


## Sugars

 - Starch: 120.02 grams
 - Fructose: 12.32 grams
 - Glucose (dextrose): 9.88 grams
 - Lactose: 5.23 grams
 - Maltose: 4.5 grams
 - Sucrose: 2.51 grams
 - Galactose: 0.56 grams


## Other



## Metals

 - Sodium, Na: 43.145 grams
 - Potassium, K: 5.503 grams
 - Calcium, Ca: 2.876 grams
 - Phosphorus, P: 2.088 grams
 - Magnesium, Mg: 0.704 grams
 - Iron, Fe: 0.09089 grams
 - Manganese, Mn: 0.025675 grams
 - Zinc, Zn: 0.02027 grams
 - Copper, Cu: 0.003438 grams
 - Selenium, Se: 0.0002409 grams
 - Fluoride, F: 0.0001124 grams


## Vitamins

 - Vitamin A, IU: 63133.0 IU
 - Vitamin D: 294.0 grams
 - Choline, total: 0.5077 grams
 - Betaine: 0.2873 grams
 - Vitamin C, total ascorbic acid: 0.0585 grams
 - Vitamin E (alpha-tocopherol): 0.03875 grams
 - Niacin: 0.034416 grams
 - Carotene, beta: 0.027021 grams
 - Lutein + zeaxanthin: 0.020214 grams
 - Tocopherol, gamma: 0.01494 grams
 - Pantothenic acid: 0.00863 grams
 - Cryptoxanthin, beta: 0.006247 grams
 - Tocotrienol, alpha: 0.00524 grams
 - Vitamin B-6: 0.005071 grams
 - Vitamin A, RAE: 0.004706 grams
 - Riboflavin: 0.004426 grams
 - Thiamin: 0.003218 grams
 - Retinol: 0.001861 grams
 - Lycopene: 0.001835 grams
 - Folate, DFE: 0.001267 grams
 - Folate, total: 0.000922 grams
 - Carotene, alpha: 0.000608 grams
 - Tocopherol, beta: 0.00056 grams
 - Folic acid: 0.000493 grams
 - Folate, food: 0.000429 grams
 - Tocopherol, delta: 0.00039 grams
 - Vitamin K (phylloquinone): 0.0002716 grams
 - Tocotrienol, gamma: 0.0001 grams
 - Tocotrienol, beta: 1e-05 grams
 - Menaquinone-4: 9.6e-06 grams
 - Vitamin D3 (cholecalciferol): 7.3e-06 grams
 - Vitamin D (D2 + D3): 7.3e-06 grams
 - Vitamin B-12: 3.18e-06 grams
 - Dihydrophylloquinone: 1e-07 grams


## Amino acids

 - Glutamic acid: 21.142 grams
 - Proline: 10.524 grams
 - Aspartic acid: 9.503 grams
 - Leucine: 7.934 grams
 - Valine: 5.319 grams
 - Lysine: 5.11 grams
 - Serine: 5.024 grams
 - Phenylalanine: 4.614 grams
 - Arginine: 4.501 grams
 - Isoleucine: 4.189 grams
 - Alanine: 3.949 grams
 - Tyrosine: 3.623 grams
 - Threonine: 3.522 grams
 - Glycine: 3.3 grams
 - Histidine: 2.23 grams
 - Methionine: 1.796 grams
 - Cystine: 1.369 grams
 - Tryptophan: 1.015 grams


## Steroids

 - Cholesterol: 0.927 grams
 - Phytosterols: 0.282 grams
 - Beta-sitosterol: 0.008 grams


## Fatty Acids

 - Fatty acids, total saturated: 139.376 grams
 - Fatty acids, total monounsaturated: 67.956 grams
 - 18:1 undifferentiated: 62.581 grams
 - 16:0: 62.062 grams
 - 18:1 c: 47.753 grams
 - 18:0: 27.299 grams
 - Fatty acids, total polyunsaturated: 26.627 grams
 - 18:2 undifferentiated: 22.581 grams
 - 14:0: 19.176 grams
 - Fatty acids, total trans: 7.809 grams
 - 4:0: 7.403 grams
 - 12:0: 7.045 grams
 - 18:2 n-6 c,c: 6.996 grams
 - Fatty acids, total trans-monoenoic: 6.962 grams
 - 18:1 t: 6.855 grams
 - 10:0: 6.164 grams
 - 6:0: 4.703 grams
 - 18:3 undifferentiated: 3.34 grams
 - 16:1 undifferentiated: 3.2 grams
 - 8:0: 2.989 grams
 - 16:1 c: 2.534 grams
 - 18:3 n-3 c,c,c (ALA): 1.951 grams
 - 17:0: 1.343 grams
 - 22:1 undifferentiated: 1.059 grams
 - 22:1 c: 1.057 grams
 - Fatty acids, total trans-polyenoic: 0.847 grams
 - 18:2 CLAs: 0.721 grams
 - 20:1: 0.666 grams
 - 18:2 i: 0.592 grams
 - 20:0: 0.403 grams
 - 15:0: 0.335 grams
 - 14:1: 0.328 grams
 - 20:4 undifferentiated: 0.269 grams
 - 18:2 t not further defined: 0.252 grams
 - 20:3 undifferentiated: 0.23 grams
 - 16:1 t: 0.107 grams
 - 22:0: 0.089 grams
 - 17:1: 0.073 grams
 - 22:6 n-3 (DHA): 0.059 grams
 - 20:3 n-6: 0.058 grams
 - 24:1 c: 0.051 grams
 - 18:4: 0.038 grams
 - 20:2 n-6 c,c: 0.037 grams
 - 22:4: 0.026 grams
 - 22:5 n-3 (DPA): 0.024 grams
 - 24:0: 0.022 grams
 - 20:3 n-3: 0.021 grams
 - 18:3 n-6 c,c,c: 0.013 grams
 - 20:5 n-3 (EPA): 0.011 grams
 - 18:3i: 0.003 grams
