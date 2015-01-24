You can grab the html of a website, but what if you only want the recipe?

![Website example](https://i.imgur.com/fjr0M6H.jpg?1)

## How it works

First it grabs the Markdown-formatted text of the html page using [html2text](https://github.com/aaronsw/html2text). 

It evalutes the number of 'cooking' related words in each line and pulls out the peak.

![Website example](https://i.imgur.com/enu0SNA.jpg?1)

It does the same for extracting the ingredient list.

Then it scans the directions and the ingredient list to determine what the *actual* baking time would be and gives that estimate.

## Example

Grab the recipe shown above from the JSON database (recipe #144,253).

```bash
python extract_recipe.py http://tastykitchen.com/recipes/sidedishes/roasted-sweet-potatoes-with-toasted-walnuts-honey-and-goat-cheese/
```

Output:

```bash
# Roasted Sweet Potatoes with Toasted Walnuts, Honey and Goat Cheese

## Ingredients

  - 4 whole Sweet Potatoes
  - 3 Tablespoons Olive Oil
  - Salt And Pepper, to taste
  - ⅓ cups Walnuts, Shelled
  - 1 Tablespoon Butter
  - 2 Tablespoons Honey
  - 2 ounces, weight Goat Cheese

## Directions

Preheat oven to 425 F.
Scrub the potatoes, and cut into chunks. Toss them in a large bowl with the
olive oil and a sprinkle of salt and pepper.
Spread them onto a rimmed baking sheet. Roast for 30 minutes at 425 F.
While the potatoes are roasting, chop up the walnuts, and heat the butter over
medium-high heat in a skillet. Add the walnuts to the pan, stirring well to
coat them completely in the melted butter. Toast for a couple of minutes,
until slightly browned. Remove pan from heat and set aside.
When the potatoes are are cooked, serve with a drizzle of honey and a sprinkle
of walnuts and goat cheese.

+ 1 minute for choping.
+ 1 minute for cuting.
+ 1 minute for tossing.
# Calculated time:  33 minute
```

## Requirements

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


Making sqlite3 fts4 virtual table
```sql
create virtual table data using fts4(ndb_no,shrt_desc);
insert into data(ndb_no,shrt_desc) select ndb_no,shrt_desc from food_des;
```