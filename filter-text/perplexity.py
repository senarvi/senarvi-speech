#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Routines for language model estimation and perplexity computation.
#
# Author: Seppo Enarvi
# http://users.marjaniemi.com/seppo/

import sys
import re
import tempfile
import subprocess


def read_word_segmentations(input_file):
	wsegs = dict()
	for line in input_file:
		line = line.strip()
		if line.startswith('#'):
			continue
		line = re.sub('\d*', '', line)
		parts = line.split(r'+')
		if len(parts) < 2:
			parts = line.split(' ')
		parts = [re.sub(' ', '', x) for x in parts]
		wrd = ''
		for part in parts:
			wrd += part
		wsegs[wrd] = parts
	return wsegs


def word_perplexity(train_text, devel_text, vocabulary=None):
	lm_file = tempfile.NamedTemporaryFile(mode='w+', encoding="utf-8")
	command = [ 'ngram-count',
			'-order', '2',
			'-wbdiscount1', '-wbdiscount2',
			'-interpolate1', '-interpolate2',
			'-text', train_text,
			'-lm', lm_file.name ]
	if vocabulary is not None:
		command.extend(['-unk', '-vocab', vocabulary])
	subprocess.check_call(command)
	
	command = [ 'ngram',
			'-order', '2',
			'-lm', lm_file.name,
			'-ppl', devel_text]
	if vocabulary is not None:
		command.extend(['-unk', '-vocab', vocabulary])
	output = subprocess.check_output(command).decode('utf-8').splitlines()
	matches = re.search(b'(\d+) OOVs', output[0])
	if matches:
		num_oovs = int(matches.group(1))
	else:
		sys.stderr.write("Unable to parse OOVs from:\n")
		sys.stderr.write(output[0])
		sys.stderr.write("\n")
		sys.exit(1)
	matches = re.search(b'ppl= ?(\d+(.\d+)?)', output[1])
	if matches:
		perplexity = float(matches.group(1))
	else:
		sys.stderr.write("Unable to parse ppl from:\n")
		sys.stderr.write(output[1])
		sys.stderr.write("\n")
		sys.exit(1)
	return perplexity, num_oovs


# Segments text according to given word segmentation, to be used as subword
# language model training data.
def segment_text(input_file, output_file, wsegs):
	for line in input_file:
		line = line.strip()
		words = line.split()
	
		output_file.write("<s> <w> ")
		for word in words:
			subwords = wsegs[word]
			for sw in subwords:
				output_file.write(sw)
				output_file.write(" ")
			output_file.write("<w> ")
		output_file.write("</s>\n")


def subword_perplexity(train_text, devel_text, wsegs, order=3):
	if wsegs is None:
		segmented_train_text = train_text
		segmented_devel_text = devel_text
	else:
		segmented_train_text = tempfile.NamedTemporaryFile(mode='w+', encoding="utf-8")
		segment_text(train_text, segmented_train_text, wsegs)
		segmented_devel_text = tempfile.NamedTemporaryFile(mode='w+', encoding="utf-8")
		segment_text(devel_text, segmented_devel_text, wsegs)
	
	lm_file = tempfile.NamedTemporaryFile(mode='w+', encoding="utf-8")
	command = [ 'ngram-count',
			'-order', str(order),
			'-wbdiscount1', '-wbdiscount2', '-wbdiscount3',
			'-interpolate1', '-interpolate2', '-interpolate3',
			'-text', segmented_train_text.name,
			'-lm', lm_file.name ]
	subprocess.check_call(command)
	
	command = [ 'perplexity',
			'-a', lm_file.name,
			'-t', '2',
			segmented_devel_text.name,
			'-']
	output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode('utf-8')
	matches = re.search('^Dropped:\s*(\d+) UNKS', output, re.MULTILINE)
	if matches:
		num_oovs = int(matches.group(1))
	else:
		sys.stderr.write("Unable to parse UNKS from:\n")
		sys.stderr.write(output)
		sys.exit(1)
	matches = re.search('^Perplexity (\d+(.\d+)?)', output, re.MULTILINE)
	if matches:
		perplexity = float(matches.group(1))
	else:
		sys.stderr.write("Unable to parse Perplexity from:\n")
		sys.stderr.write(output)
		sys.exit(1)
	return perplexity, num_oovs
