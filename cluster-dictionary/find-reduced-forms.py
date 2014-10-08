#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Reads a colloquial and a standard Finnish vocabulary, and for each (reduced)
# word form that exists only in the colloquial vocabulary (e.g. "sitkö"), finds
# its base form (e.g. "sittenkö").

import argparse
import sys
from copy import deepcopy
from filetypes import TextFileType
from editpartitioning import EditPartitioning
from finnishreductions import validate

parser = argparse.ArgumentParser()
parser.add_argument('svocab', type=TextFileType('r'), help='standard Finnish vocabulary')
parser.add_argument('cvocab', type=TextFileType('r'), help='conversational Finnish vocabulary')
parser.add_argument('--consider-std-words', action='store_true', default=False, help='consider also words that exist in the standard Finnish vocabulary')
args = parser.parse_args()

# Standard Finnish vocabulary grouped by initial letter of word.
std_vocab = dict()
for line in args.svocab:
	word = line.rstrip()
	initial_letter = word[0]
	if initial_letter in std_vocab:
		std_vocab[initial_letter].add(word)
	else:
		std_vocab[initial_letter] = set([word])
args.svocab.close()

# Conversational Finnish vocabulary as continuous list.
con_vocab = [line.rstrip() for line in args.cvocab]
args.cvocab.close()

# Combined standard and conversational vocabulary as continuous list.
full_vocab = deepcopy(std_vocab)
for word in con_vocab:
	initial_letter = word[0]
	if initial_letter in full_vocab:
		full_vocab[initial_letter].add(word)
	else:
		full_vocab[initial_letter] = set([word])

for con_word in con_vocab:
	if len(con_word) < 2:
		continue
	initial_letter = con_word[0]
	# Check that this is not a standard Finnish word.
	if (not args.consider_std_words) and (initial_letter in std_vocab) and (con_word in std_vocab[initial_letter]):
		continue
	peers = []
	# We only need to validate against words that have the same initial letter.
	for std_word in full_vocab[initial_letter]:
		edits = EditPartitioning(std_word, con_word)
		edits.clean()
		if validate(edits.partitions):
			peers.append(std_word)
	if len(peers) > 0:
		print(con_word, " ".join(peers))
		sys.stdout.flush()

