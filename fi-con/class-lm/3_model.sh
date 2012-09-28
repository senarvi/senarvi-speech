#!/bin/sh

# The text with words replaced with their classes:
TRAIN_TEXT_C="$WORK_DIR/fi-all-train-classes.txt.gz"
cat $ALL_TEXTS \
| replace-words-with-classes "classes=$CLASSES" - \
| "$SCRIPTDIR/replace-oovs-with-class.pl" \
>"$TEXT_CLASSES"
