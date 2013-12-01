#!/usr/bin/env python3
#
# Compares the original hypothesis, and hypotheses from reductions files (i.e. those
# where one word has been reduced from the lattice), to a reference transcription.
#
# Expects an input reductions file that contains the original hypothesis in the first
# line, and the one-word-out hypotheses in the subsequent lines (preceded by the word
# that was omitted).
#
# The output will contain the number of words in the original hypothesis and the
# original score in the first line, and the one-word-out scores in the subsequent
# lines (preceded by the word that was omitted).

import argparse
import os
import sys
import subprocess
import re
from operator import itemgetter
from filetypes import TextFileType

def evaluate_hypothesis(hypothesis, utterance_id, score_command):
	hypothesis = hypothesis.split()
	hypothesis = [x for x in hypothesis if not ((x == "<s>") or (x == "</s>"))]
	hypothesis = " ".join(hypothesis) + " (" + str(utterance_id) + ")"
	proc = subprocess.Popen(score_command, \
						stdin=subprocess.PIPE, \
						stdout=subprocess.PIPE)
	proc.stdin.write(hypothesis.encode('utf-8'))
	proc.stdin.close()
	result = proc.stdout.readline().split()
	if len(result) != 2:
		raise Exception("Invalid result from score command.")
	return int(result[0]), int(result[1])

def update_errors(red_file, utterance_id, score_command):
	lines = red_file.readlines()

	if len(lines) == 0:
		sys.stderr.write("Empty reductions file: " + red_file.name + "\n")
		sys.exit(1)
	
	num_words, original_err = evaluate_hypothesis(lines[0], utterance_id, score_command)
	sys.stdout.write(str(num_words) + " " + str(original_err) + "\n")
	
	for line in lines[1:]:
		if len(line) == 0:
			continue
		separator_pos = line.find(" ")
		if separator_pos == -1:
			word = line
			hypothesis = ""
		else:
			word = line[0:separator_pos]
			hypothesis = line[separator_pos + 1:]
		_, err = evaluate_hypothesis(hypothesis, utterance_id, score_command)
		sys.stdout.write(word + " " + str(err) + "\n")

parser = argparse.ArgumentParser()
parser.add_argument('scorecommand', type=str, help='a command that reads a sentence and writes a score')
parser.add_argument('inputfile', type=TextFileType('r'), help='the input reductions file')
args = parser.parse_args()

file_name = os.path.basename(args.inputfile.name)
utterance_id, _ = os.path.splitext(file_name)
update_errors(args.inputfile, utterance_id, args.scorecommand)
