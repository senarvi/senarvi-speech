#!/bin/sh
#
# Take the same amount of training data from Kielipankki.

WORK_DIR="/share/work/senarvi/class-lm"

zcat /share/puhe/jpylkkon/kielipankki/traindata.txt.gz \
| grep -v '^FILE' \
| tail -5000000 \
| head -70195 \
| recode 'ISO-8859-1..UTF-8' \
> "$WORK_DIR/fi-lit.txt"
