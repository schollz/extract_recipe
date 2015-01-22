from nltk.corpus import wordnet
import sys
from pattern.en import singularize
import string
exclude = set(string.punctuation)

words = sys.argv[1:]
index = 0
done = False
for word in words:
  word = ''.join(ch for ch in word if ch not in exclude)
  word = word.lower()
  word = singularize(word)
  synsets = wordnet.synsets(word)
  for synset in synsets:
    if 'quantity' in synset.lexname:
      done = True
  if done:
    break
  index = index + 1

quantities = [words[index],words[index+1]]
print quantities

words = words[2:]
indices = []
index = 0
done = False
for word in words:
  word = ''.join(ch for ch in word if ch not in exclude)
  word = word.lower()
  word = singularize(word)
  synsets = wordnet.synsets(word)
  if len(synsets)<4:
    for synset in synsets:
      '''print "-" * 10
      print "Name:", synset.name
      print "Lexical Type:", synset.lexname
      print "Lemmas:", synset.lemma_names
      print "Definition:", synset.definition
      for example in synset.examples:
        print "Example:", example'''
      if 'food' in synset.lexname:
        indices.append(index)
        break
  index = index + 1

foods = indices
for index in indices:
  print [words[index]]
  if index > 0:
    print [words[index-1],words[index]]
  if index < len(words)-1:
    print [words[index],words[index+1]]
  


