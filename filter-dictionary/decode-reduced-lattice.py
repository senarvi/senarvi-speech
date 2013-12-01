#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Syntax: decode-reduced-lattice.py [lattice] [--exclude word1 word2 ...] [--exclude-individually word1 word2 ...]
#
# Evaluates a word lattice after removing a number of words from it.
#
# First removes all the words given with --exclude command line argument from the
# lattice. Decodes the lattice using lattice-tool, and writes the result on the
# first output line, e.g. "<s> the sun has now set </s>". Then, one by one removes
# the words given with --exclude-individually command line argument. Each word
# excluded, decodes the lattice and writes the result on a separate line, preceded
# by the word that was excluded, e.g. "sun <s> the son has now set </s>".
#
# If the end node is not reachable, the sentence will be empty, but the line
# will still be printed.

import argparse
import sys
import codecs
import os
import tempfile
import subprocess
from wordlattice import WordLattice
from filetypes import TextFileType

def decode_lattice(lattice):
	script_dir = os.path.dirname(os.path.realpath(__file__))
	executable = os.path.join(script_dir, 'decode-lattice.sh')

	if lattice.end_node == -1:
		return ""

	slf_file = tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8')
	lattice.write_slf(slf_file)
	slf_file.flush()
	command = [executable, slf_file.name]
	proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	output, errors = proc.communicate()
	output = output.decode('utf-8')
	errors = errors.decode('utf-8')
	if proc.returncode:
		raise Exception(' '.join(command) + " failed with code %s" % proc.returncode)
	for line in errors.splitlines():
		if "warning" in line:
			continue
		# The end node was unreachable.
		return ""
	return output.rstrip()

parser = argparse.ArgumentParser()
parser.add_argument('lattice', type=TextFileType('r'), help='a lattice file')
parser.add_argument('--exclude', dest='exclude_always', metavar='word', type=str, nargs='*', default=[],
                   help='words to exclude from every decoding')
parser.add_argument('--exclude-individually', dest='exclude_once', metavar='word', type=str, nargs='*', default=[],
                   help='words to exclude individually, each word once, or ! for all the words in the original hypothesis')
args = parser.parse_args()

lattice = WordLattice()
lattice.read_slf(args.lattice)
args.lattice.close()

sentence_boundaries = set(['<s>', '</s>'])

exclude_always = set(args.exclude_always) - sentence_boundaries
lattice.remove_words(exclude_always)
hypothesis = decode_lattice(lattice)
sys.stdout.write(hypothesis + "\n")

if "!" in args.exclude_once:
	exclude_once = set(hypothesis.split())
else:
	exclude_once = set(args.exclude_once)
exclude_once -= exclude_always
exclude_once -= sentence_boundaries

for word in exclude_once:
	reduced_lattice = lattice.without_words([word])
	hypothesis = decode_lattice(reduced_lattice)
	sys.stdout.write(word + " " + hypothesis + "\n")
