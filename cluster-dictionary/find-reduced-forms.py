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
parser.add_argument(
    'svocab', type=TextFileType('r'),
    help='standard Finnish vocabulary')
parser.add_argument(
    'cvocab', type=TextFileType('r'),
    help='conversational Finnish vocabulary')
parser.add_argument(
    '--consider-std-words', action='store_true', default=False,
    help='consider also words that exist in the standard Finnish vocabulary')
parser.add_argument(
    '--num-jobs', metavar='J', type=int, default=1,
    help='divide the conversational words into J distinct batches, and '
         'process only batch I')
parser.add_argument(
    '--job', metavar='I', type=int, default=0,
    help='the index of the batch that this job should process, between 0 '
         'and J-1')
parser.add_argument(
    '--output-file', metavar='FILE', type=TextFileType('w'), default='-',
    help='where to write the word lists (default stdout, will be compressed if '
         'the name ends in ".gz")')
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

# Pick every Ith word, if --num-jobs is specified and > 1.
if args.num_jobs < 1:
    print("Invalid number of jobs specified:", args.num_jobs)
    sys.exit(1)
if (args.job < 0) or (args.job > args.num_jobs - 1):
    print("Invalid job specified:", args.job)
    sys.exit(1)
con_vocab = con_vocab[args.job::args.num_jobs]

for index, con_word in enumerate(con_vocab):
    if len(con_word) < 2:
        continue
    initial_letter = con_word[0]
    # Check that this is not a standard Finnish word.
    if (not args.consider_std_words) and \
       (initial_letter in std_vocab) and \
       (con_word in std_vocab[initial_letter]):
        continue
    peers = []
    # We only need to validate against words that have the same initial letter.
    for std_word in full_vocab[initial_letter]:
        edits = EditPartitioning(std_word, con_word)
        edits.clean()
        if validate(edits.partitions):
            peers.append(std_word)
    if len(peers) > 0:
        args.output_file.write("{} {}\n".format(con_word, " ".join(peers)))
        args.output_file.flush()
    print("{} / {} ({} %)".format(index,
                                  len(con_vocab),
                                  index / len(con_vocab) * 100))
    sys.stdout.flush()
