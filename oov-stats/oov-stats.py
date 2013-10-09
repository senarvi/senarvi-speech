#!/usr/bin/env python3
#
# Reads a vocabulary and a corpus. While reading the corpus, periodically
# outputs statistics of vocabulary size and OOV rate. 

from optparse import OptionParser
import sys
import io

def print_stats(counts, word_limit):
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
					del counts[word]
			word_count += 1
			if word_count % 100000 == 0:
				oov_rate = float(num_oov_words) / num_test_words
				sys.stdout.write("%i, %i, %i, %f\n" % (word_count, len(vocabulary), num_oov_words, oov_rate))
				sys.stderr.write("word_count=%i, vocabulary=%i, num_oov_words=%i, oov_rate=%f\n" % (word_count, len(vocabulary), num_oov_words, oov_rate))
			if word_count > word_limit:
				return

parser = OptionParser()
parser.add_option('--limit',
                  action='store', type='int', dest='limit', default=None)
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

print_stats(counts, options.limit)

sorted_counts = sorted(counts, key=counts.get)
sys.stderr.write("Most frequent unseen words:\n")
for i in range(1, min(11, len(counts))):
	word = sorted_counts[-i]
	count = counts[word]
	sys.stderr.write(word + ", " + str(count) + " occurrences\n")
