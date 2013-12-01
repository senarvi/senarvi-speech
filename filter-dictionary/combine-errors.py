#!/usr/bin/env python
#
# Compares the original hypothesis, and one-word-out transcriptions, to a
# reference transcription.
#
# Expects an input file with the original hypothesis in the first line, and the
# one-word-out transcriptions in the subsequent lines (preceded by the word that
# was omitted).

import argparse
import os
import sys
import subprocess
import re
from operator import itemgetter

def update_errors(red_path, utterance_id, word_errors):
	with open(red_path, 'r') as red_file:
		lines = red_file.readlines()

	if len(lines) == 0:
		sys.stderr.write("Empty reduction scores file: " + red_path + "\n")
		sys.exit(1)
	
	line = lines[0]
	separator_pos = line.find(" ")
	if separator_pos == -1:
		sys.stderr.write("Invalid reduction scores file: " + red_path + "\n")
		sys.exit(1)
	num_words = int(line[0:separator_pos])
	original_err = int(line[separator_pos + 1:])
	
	for line in lines[1:]:
		if len(line) == 0:
			continue
		separator_pos = line.find(" ")
		if separator_pos == -1:
			sys.stderr.write("Invalid reduction scores file: " + red_path + "\n")
			sys.exit(1)
		else:
			word = line[0:separator_pos]
			err = int(line[separator_pos + 1:])
		
		result = str(num_words) + ":" + str(original_err) + ":" + str(err)
		if word in word_errors:
			word_errors[word].append(result)
		else:
			word_errors[word] = [result]

parser = argparse.ArgumentParser()
parser.add_argument('rootdir', type=str, help='path to the root directory of reduction score files')
args = parser.parse_args()

word_errors = {}

for dir, subdirs, files in os.walk(args.rootdir):
	for file_name in files:
		utterance_id, extension = os.path.splitext(file_name)
		if extension == '.redsc':
			sys.stderr.write(utterance_id + "\n")
			update_errors(os.path.join(dir, file_name), utterance_id, word_errors)

for word, results in sorted(word_errors.items(), key=itemgetter(1)):
	sys.stdout.write(word)
	for utterance_result in results:
		sys.stdout.write(" " + utterance_result)
	sys.stdout.write("\n")
