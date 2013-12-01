#!/usr/bin/env python3
#
# Find the worst scoring word pronunciation based on an errors file. There is
# one line per word pronunciation in the errors file. Each line begins with
# the word name, including optional pronunciation ID. Followed by the word
# name is one entry per training utterance that gives information about the
# word errors in the utterance. The format is:
#
#   WORD[:N] WORDS1:ORIGERR1:ERR1 WORDS2:ORIGERR2:ERR2 ...
#
# :N indicates Nth pronunciation variant, and is only given for words with
# multiple pronunciation variants. WORDSi is the number of words in the ith
# utterance. ORIGERRi is the number of word errors in the best path of the
# original pronunciation lattice. ERRi is the number of word errors in the
# best path of the pronunciation lattice without WORD:N.

import argparse
import sys
import codecs
from filetypes import TextFileType

parser = argparse.ArgumentParser()
parser.add_argument('errors', type=TextFileType('r'), help='input errors file')
parser.add_argument('--add-one-smoothing', action='store_true', default=False, help='add one to total error increase for each word')
parser.add_argument('--algorithm', type=str, default="wer_dec", help='scoring algorithm (err_dec = total error decrease, wer_dec = average error decrease per utterance)')
parser.add_argument('--max-err-inc', type=int, default=9999, help='set a maximum for error increase per utterance')
args = parser.parse_args()

worst_score = 0
for line in args.errors:
	fields = line.split()
	if len(fields) == 0:
		continue
	word = fields[0]
		
	total_err_inc = 0
	total_wer_inc = 0
	num_utterances = 0
	for entry in fields[1:]:
		entry = entry.split(':')
		if len(entry) != 3:
			raise Exception("Unable to parse errors entry.")
		num_words = int(entry[0])
		orig_err = int(entry[1])
		err = int(entry[2])
		err_inc = err - orig_err
		err_inc = min(err_inc, args.max_err_inc)
		total_err_inc += err_inc
		if num_words > 0:
			wer_inc = float(err_inc) / num_words
			total_wer_inc += wer_inc
		num_utterances += 1
		
	if args.add_one_smoothing:
		total_err_inc += 1
		total_wer_inc += 0.01
		num_utterances += 1
		
	if num_utterances > 0:
		avg_err_inc = float(total_err_inc) / num_utterances
		avg_wer_inc = float(total_wer_inc) / num_utterances
		if args.algorithm == "err_dec":
			if avg_err_inc < worst_score:
				worst_score = avg_err_inc
				worst_word = word
		elif args.algorithm == "wer_dec":
			if avg_wer_inc < worst_score:
				worst_score = avg_wer_inc
				worst_word = word
		else:
			raise Exception("Unknown algorithm: " + args.algorithm)

if worst_score < 0:
	sys.stdout.write(worst_word + "\n")
