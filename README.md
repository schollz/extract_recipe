You can grab the html of a website, but what if you only want the recipe?

![Website example](https://i.imgur.com/fjr0M6H.jpg?1)

## How it works

Uses the [openrecipe](https://github.com/fictivekin/openrecipes) JSON dump, which you can download [here](http://openrecipes.s3.amazonaws.com/recipeitems-latest.json.gz).

First it grabs the Markdown-formatted text of the html page using [html2text](https://github.com/aaronsw/html2text). 

Then it evalutes the number of 'cooking' related words in each line and pulls out the peak.

![Website example](https://i.imgur.com/enu0SNA.jpg?1)

## Example

Grab the 1st recipe from the JSON database.

```bash
python extract_recipe.py 1
```

Output:

```bash
Preheat oven to 400 degrees.

Add flour, baking powder, and salt to the bowl of a food processor (or a large
bowl.) Add butter pieces and pulse until butter is completely cut into the
flour mixture (or use a pastry cutter if using a bowl.) While pulsing (or
stirring) drizzle in the buttermilk until dough just comes together and is no
longer crumbly.

Drop in clumps on two baking sheets, then bake for 15-17 minutes, or until
golden brown. (Optional: Brush with melted butter when biscuits first come out
of the oven.)

SAUSAGE GRAVY

With your finger, tear small pieces of sausage and add them in a single layer
to a large heavy skillet. Brown the sausage over medium-high heat until no
longer pink. Reduce the heat to medium-low. Sprinkle on half the flour and
stir so that the sausage soaks it all up, then add a little more until just
before the sausage looks too dry. Stir it around and cook it for another
minute or so, then pour in the milk, stirring constantly.

Cook the gravy, stirring frequently, until it thickens. (This may take a good
10-12 minutes.) Sprinkle in the seasoned salt and pepper and continue cooking
until very thick and luscious. If it gets too thick too soon, just splash in
1/2 cup of milk or more if needed. Taste and adjust seasonings.

Spoon sausage gravy over warm biscuits and serve immediately!

Posted by Ree | The Pioneer Woman on March 11 2013
```
