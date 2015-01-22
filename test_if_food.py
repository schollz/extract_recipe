from nltk.corpus import wordnet
import sys

synsets = wordnet.synsets(sys.argv[1])

for synset in synsets:
  print "-" * 10
  print "Name:", synset.name
  print "Lexical Type:", synset.lexname
  print "Lemmas:", synset.lemma_names
  print "Definition:", synset.definition
  for example in synset.examples:
    print "Example:", example
