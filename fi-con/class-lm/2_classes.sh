#!/bin/sh
#
# Estimate classes and create a training text for class-based models.

WORK_DIR="/share/work/senarvi/class-lm"
VOCAB_DIR="/share/work/senarvi/vocabularies"

CON_TEXTS="/share/puhe/text/fin-dialogue/*.txt /share/puhe/text/kotus-hsl/*.txt"
LIT_TEXTS="$WORK_DIR/fi-lit.txt"
ALL_TEXTS="$CON_TEXTS $LIT_TEXTS"

# Target number of classes in the class-based models. I've selected half the
# size of the vocabulary.
NUM_CLASSES=24305

VOCAB="$VOCAB_DIR/fi-all-49k.vocab"
# Class members and their probabilities:
CLASSES="/home/senarvi/experiments/class-lm/fi-all.classes"
# Counts for class bigrams:
CLASS_COUNTS="/home/senarvi/experiments/class-lm/fi-all.class-counts"
cat $ALL_TEXTS \
| ngram-class -vocab "$VOCAB" -text - -numclasses $NUM_CLASSES -class-counts "$CLASS_COUNTS" -classes "$CLASSES" -save 100 -debug 2

VOCAB="$VOCAB_DIR/fi-con-28k.vocab"
# Class members and their probabilities:
CLASSES="/home/senarvi/experiments/class-lm/fi-con.classes"
# Counts for class bigrams:
CLASS_COUNTS="/home/senarvi/experiments/class-lm/fi-con.class-counts"
#cat $CON_TEXTS \
#| ngram-class -vocab "$VOCAB" -text - -numclasses $NUM_CLASSES -class-counts "$CLASS_COUNTS" -classes "$CLASSES" -save 100 -debug 2

VOCAB="$VOCAB_DIR/fi-lit-28k.vocab"
# Class members and their probabilities:
CLASSES="/home/senarvi/experiments/class-lm/fi-all.classes"
# Counts for class bigrams:
CLASS_COUNTS="/home/senarvi/experiments/class-lm/fi-all.class-counts"
zcat /share/puhe/jpylkkon/kielipankki/traindata.txt.gz \
| grep -v '^FILE' \
| recode 'ISO-8859-1..UTF-8' \
| ngram-class -vocab "$VOCAB" -text - -numclasses $NUM_CLASSES -class-counts "$CLASS_COUNTS" -classes "$CLASSES" -save 100 -debug 2
