add-synonyms-to-classes.py
==========================

Reads a class definitions file and a list of synonyms. Then adds the synonyms
to the corresponding class, gives it the same probability as its synonym, and
normalizes the total probability to 1.


cat-classes.py
==============

Concatenates class definition files and renames the classes so that class
definitions from different files will be uniquely named.


fix-class-probabilities.py
==========================

Reads a class definitions file and an n-gram counts file, and corrects the
class expansion probabilities according to the unigram counts of the words.


interpolate-lm.py
=================

Computes the optimal mixture (in terms of devel text perplexity) of language
models, and creates an interpolated language model using SRILM.


ngramcounts.py
==============

A Python class that stores n-gram counts.


wordclasses.py
==============

A Python class that stores word class definitions.
