You can grab the html of a website, but what if you only want the recipe?

![Website example](https://i.imgur.com/fjr0M6H.jpg?1)

## How it works

First it grabs the Markdown-formatted text of the html page using [html2text](https://github.com/aaronsw/html2text). 

Then it evalutes the number of 'cooking' related words in each line and pulls out the peak.

![Website example](https://i.imgur.com/enu0SNA.jpg?1)

## Example

```bash
python extract_recipe.py http://tastykitchen.com/recipes/sidedishes/roasted-sweet-potatoes-with-toasted-walnuts-honey-and-goat-cheese/
```

Output:

```bash
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

### More Recipes from LuAnne

#### London Broil

```
