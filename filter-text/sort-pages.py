#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Sorts the search results based on perplexity or similar measure calculated
# by a subprocess on a text. Possibly trains a language model on more and more
# text, calculating the perplexity on a development set, and writing the
# statistics to a CSV file.
#
# When the switch --write-scores is given, displays the scores with the pages,
# so that one can manually select a filtering threshold.
#
# If a development text is given with the --devel-text option, estimates a
# language model from the output text every N pages, and writes perplexity and
# OOV rate of the development text to a CSV file (this requires SRILM tools).
# If also a word segmentation file is given with the --word-seg option, uses
# subword perplexity (this requires the variKN tools). N is selected so that
# perplexity will be calculated at most 500 times.
#
# Author: Seppo Enarvi
# http://users.marjaniemi.com/seppo/

import argparse
import sys
import io
import operator
import subprocess
import tempfile
from pages import *
from perplexity import *
from filetypes import TextFileType

parser = argparse.ArgumentParser()
parser.add_argument('scores', type=TextFileType('r'), help='input scores file')
parser.add_argument('input', type=TextFileType('r'), nargs='+', help='input text page files')
parser.add_argument('--output', type=TextFileType('w'), default='-', help='output file for sorted text pages')
parser.add_argument('--in-memory', action='store_true', default=False, help='load the entire data set into memory')
parser.add_argument('--merge-fragments', action='store_true', default=False, help='merge pages whose URI only differs after fragment identifier')
parser.add_argument('--descending', action='store_true', default=False, help='sort pages in descending order')
parser.add_argument('--include', type=int, default=None, help='output only this many pages')
parser.add_argument('--write-scores', action='store_true', default=False, help='also output scores')
parser.add_argument('--devel-text', type=TextFileType('r'), default=None, help='periodically estimate a language model and compute its perplexity on this text')
parser.add_argument('--word-seg', type=TextFileType('r'), default=None, help='use this segmentation to segment words into subwords before computing perplexities with variKN')
parser.add_argument('--text-is-subwords', action='store_true', default=False, help='computes perplexities using variKN, assuming the text is already subwords')
parser.add_argument('--order', type=int, default=3, help='language model order for perplexity computations')
parser.add_argument('--vocab', type=str, default=None, help='vocabulary for word-based perplexity computations')
parser.add_argument('--statistics', type=TextFileType('w'), dest='statistics', default=None, help='where to write the CSV statistics to')
args = parser.parse_args()

uris = set()
pages = dict()
for input_file in args.input:
	for page in read_pages(input_file, not args.merge_fragments):
		uri = page.uri()
		uris.add(uri)
		if args.in_memory:
			if uri in pages:
				pages[uri] += page.content()
			else:
				pages[uri] = page.content()
	if args.in_memory:
		input_file.close()

sys.stderr.write("%i pages in the input files.\n" % len(uris))
if args.include is None:
	args.include = len(uris)

scores = read_scores(args.scores)
sys.stderr.write("Read %i scores.\n" % len(scores))
sorted_scores = sorted(scores.items(), key=operator.itemgetter(1), reverse=args.descending)

if args.word_seg is not None:
	wsegs = read_word_segmentations(args.word_seg)
	sys.stderr.write("Read %i word segmentations.\n" % len(wsegs))
else:
	wsegs = None

if (args.devel_text is not None) and (args.statistics is not None):
	train_text = tempfile.NamedTemporaryFile(mode='w+', encoding="utf-8")
	
	args.statistics.write("pages, threshold score, perplexity, OOVs\n")
	
	page_count = 0
	stats_count = 0
	for uri, score in sorted_scores:
		if not uri in uris:
			continue
		if args.in_memory:
			train_text.write(pages[uri])
		else:
			for input_file in args.input:
				input_file.seek(0)
				write_matching_content(input_file, train_text, uri, args.merge_fragments)
		page_count += 1
		if page_count >= len(uris) / 500 * stats_count:
			stats_count += 1
			try:
				train_text.flush()
				if args.text_is_subwords:
					train_text.seek(0)
					perplexity, num_oovs = subword_perplexity(train_text, args.devel_text, None, args.order)
					train_text.seek(0, 2)
				elif wsegs is not None:
					train_text.seek(0)
					perplexity, num_oovs = subword_perplexity(train_text, args.devel_text, wsegs, args.order)
					train_text.seek(0, 2)
				else:
					perplexity, num_oovs = word_perplexity(train_text.name, args.devel_text, args.vocab)
				stats_file.write("%i, %f, %f, %i\n" % (page_count, score, perplexity, num_oovs))
				stats_file.flush()
				sys.stderr.write("page_count=%i, score=%f, perplexity=%f, num_oovs=%i\n" % (page_count, score, perplexity, num_oovs))
			except subprocess.CalledProcessError as e:
				# Currently perplexity computation may fail if there are no
				# 3-grams yet in the training data. Just continue.
				sys.stderr.write("Unable to compute perplexity yet. Continuing.\n")
		if page_count >= args.include:
			break

elif args.output is not None:
	page_count = 0
	for uri, score in sorted_scores:
		if not uri in uris:
			continue
		page_count += 1
		if args.in_memory:
			args.output.write(pages[uri])
		else:
			try:
				if args.write_scores:
					sys.stdout.write("###### score=" + str(score) + "\n")
				for input_file in args.input:
					input_file.seek(0)
					write_matching_content(input_file, args.output, uri, args.merge_fragments)
			except IOError:
				# Silently ignore write errors, since we'll get a SIGPIPE if the
				# output is piped to head.
				sys.exit(1)
		if (args.include is not None) and (page_count >= args.include):
			break

