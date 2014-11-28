#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Efficient implementation of scoring segments of language model training
# text, based on log probability given by the language model on an in-domain
# development text when a segment is removed from the training set. The
# algorithm is based on [Klakow 2000], but with the following optimizations:
#
# - Instead of computing the change in log probability when a page is removed
#   from the training set, we simply compute the new log probability, since
#   the probability given by the entire training set is constant and won't
#   affect the selection.
# - Only unigram maximum likelihood probabilities are supported. Thus we need
#   to collect only word counts.
# - As we only use the model to evaluate the development text, we only need
#   to collect counts for those individual words that occur in the development
#   text. (We also need the total word count.)
# - The counts in the entire training text are collected only once. Then we
#   proceed by collecting the counts of each individual segment at a time,
#   and subtracting them from the counts of the entire training text.
#
# Author: Seppo Enarvi
# http://users.marjaniemi.com/seppo/

import argparse
import sys
import re
import math
from pages import *
from filetypes import TextFileType

def add_unigram_counts(text, counts, vocab):
	total = 0
	for word in text.split():
		if word in counts:
			counts[word] += 1
		elif (vocab is None) or (word in vocab):
			counts[word] = 1
		total += 1
	return counts, total

def read_unigram_counts(file, vocab=None):
	counts = dict()
	total = 0
	for line in file:
		if not line.startswith('###### '):
			counts, line_total = add_unigram_counts(line, counts, vocab)
			total += line_total
	return counts, total

parser = argparse.ArgumentParser()
parser.add_argument('pages', type=TextFileType('r'), help='non-domain-specific input text pages')
parser.add_argument('idtext', type=TextFileType('r'), help='in-domain development text')
parser.add_argument('--scores', type=TextFileType('w'), default='-', help='output scores file')
parser.add_argument('-B', '--batch', type=int, dest='num_batches', default=1, help='number of batches to split the job into')
parser.add_argument('-I', '--bindex', type=int, dest='batch_index', default=1, help='index of this batch, starting from 1')
args = parser.parse_args()

if args.batch_index > args.num_batches:
	sys.stderr.write("Batch index has to be smaller than or equal to the number of batches.\n")
	sys.exit(2)
if args.batch_index < 1:
	sys.stderr.write("Batch indices start from 1.\n")
	sys.exit(2)

id_counts, _ = read_unigram_counts(args.idtext)
args.idtext.close()

vocabulary = id_counts.keys()
sys.stderr.write('%d words in in-domain text.\n' % len(vocabulary))

nds_counts, nds_total = read_unigram_counts(args.pages, vocabulary)
vocabulary = [word for word in vocabulary if word in nds_counts]
sys.stderr.write('%d in-domain words in training data.\n' % len(vocabulary))

args.pages.seek(0)
page_index = -1
for page in read_pages(args.pages):
	page_index += 1
	if page_index % args.num_batches + 1 != args.batch_index:
		continue
	uri = page.uri()
	page_counts, page_total = add_unigram_counts(page.content(), dict(), vocabulary)
	sub_total = nds_total - page_total
	logprob = 0
	for word in vocabulary:
		sub_count = nds_counts[word]
		if word in page_counts:
			sub_count -= page_counts[word]
		if sub_count < 1:
			logprob = -sys.float_info.max
			break
		else:
			id_count = id_counts[word]
			try:
				logprob += math.log(float(sub_count) / sub_total) * id_count
			except ValueError:
				sys.stderr.write('At page "%s":\n' % uri)
				sys.stderr.write('Error computing log(%d / %d) * %d.\n' % (sub_count, sub_total, id_count))
	args.scores.write(page.header())
	args.scores.write(str(logprob) + '\n')
