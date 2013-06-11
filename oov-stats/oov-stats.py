#!/usr/bin/env python3
#
# Reads a pronunciation dictionary and an errors file. There is one line per
# word pronunciation in the errors file. Each line begins with the word name,
# including optional pronunciation ID. Followed by the word name is one entry
# per training utterance that gives information about the word errors in the
# utterance. The format is:
#
#   WORD[:N] WORDS1:ORIGERR1:ERR1 WORDS2:ORIGERR2:ERR2 ...
#
# :N indicates Nth pronunciation variant, and is only given for words with
# multiple pronunciation variants. WORDSi is the number of words in the
# ith utterance. ORIGERRi is the number of word errors in the best path of the
# original pronunciation lattice. ERRi is the number of word errors in the best
# path of the pronunciation lattice without WORD:N.
#
# This script converts the word errors into pronunciation probabilities
# (avg_err_inc or avg_wer_inc algorithm), or removes words that cause more
# errors (err_dec or wer_dec algorithm), and writes a new dictionary.

from optparse import OptionParser
import sys
import io

parser = OptionParser()
(options, args) = parser.parse_args()

if len(args) != 1:
	print >>sys.stderr, "Expecting path to test data."
	sys.exit(2)

counts = {}
with open(args[0], 'r', encoding='utf-8') as f:
	for line in f:
		for word in line.split():
			if not word in counts:
				counts[word] = 1
			else:
				counts[word] += 1

num_test_words = sum(counts.values())
num_oov_words = num_test_words

vocabulary = set()
word_count = 0
sys.stdout.write("corpus size, unique words, unseen words, OOV rate\n")
for line in io.TextIOWrapper(sys.stdin.buffer, 'utf-8'):
	for word in line.split():
		if not word in vocabulary:
			vocabulary.add(word)
			if word in counts:
				num_oov_words -= counts[word]
		word_count += 1
		if word_count % 100000 == 0:
			oov_rate = float(num_oov_words) / num_test_words
			sys.stdout.write("%i, %i, %i, %f\n" % (word_count, len(vocabulary), num_oov_words, oov_rate))
			sys.stderr.write("word_count=%i, vocabulary=%i, num_oov_words=%i, oov_rate=%f\n" % (word_count, len(vocabulary), num_oov_words, oov_rate))
