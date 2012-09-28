#!/bin/sh
#
# Create vocabularies.

VOCAB_DIR="/share/work/senarvi/vocabularies"

mkdir -p "$VOCAB_DIR"

cat /share/puhe/text/fin-dialogue/*.txt \
| ngram-count -order 1 -text - -write - \
| sort -k 2 -g -r \
| grep -v '\[reject\]' \
| grep '^[a-zäöå]' \
| grep -v '\-\s' \
>"$VOCAB_DIR/fin-dialogue.word-counts"

cat /share/puhe/text/kotus-hsl/*.txt \
| ngram-count -order 1 -text - -write - \
| sort -k 2 -g -r \
| grep -v '\[reject\]' \
| grep '^[a-zäöå]' \
| grep -v '\-\s' \
>"$VOCAB_DIR/kotus-hsl.word-counts"

head -6230 "$VOCAB_DIR/fin-dialogue.word-counts" \
| cut -f1 \
| sort \
>"$VOCAB_DIR/fin-dialogue.vocab"

head -25696 "$VOCAB_DIR/kotus-hsl.word-counts" \
| cut -f1 \
| sort \
>"$VOCAB_DIR/kotus-hsl.vocab"

cat "$VOCAB_DIR/fin-dialogue.vocab" "$VOCAB_DIR/kotus-hsl.vocab" \
| sort -u \
>"$VOCAB_DIR/fi-con-28k.vocab"

# All words that occur at least 100 times.
zcat /share/puhe/jpylkkon/kielipankki/traindata.vocab.gz \
| recode 'ISO-8859-1..UTF-8' \
| cut -f2 \
| head -99942 \
>"$VOCAB_DIR/fi-lit-100k.vocab"

zcat /share/puhe/jpylkkon/kielipankki/traindata.vocab.gz \
| recode 'ISO-8859-1..UTF-8' \
| cut -f2 \
| head -28426 \
>"$VOCAB_DIR/fi-lit-28k.vocab"

cat "$VOCAB_DIR/fi-con-28k.vocab" "$VOCAB_DIR/fi-lit-28k.vocab" \
| sort -u \
>"$VOCAB_DIR/fi-all-49k.vocab"
