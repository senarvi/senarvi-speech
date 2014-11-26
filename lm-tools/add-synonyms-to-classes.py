#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Reads a class definitions file and a list of synonyms. Then adds the synonyms
# to the corresponding class, gives it the same probability as its synonym, and
# normalizes the total probability to 1.

import argparse
import sys
from filetypes import TextFileType
from wordclasses import WordClasses

parser = argparse.ArgumentParser()
parser.add_argument('classes', type=TextFileType('r'), help='input class definitions file')
parser.add_argument('synonyms', type=TextFileType('r'), help='file containing a list of synonyms')
args = parser.parse_args()

classes = WordClasses()
classes.read(args.classes)

for line in args.synonyms:
	words = line.split()
	if len(words) == 0:
		continue
	if len(words) != 2:
		raise Exception("Invalid line in synonyms file: " + line)
	cls = classes.find_containing(words[0])
	if cls is None:
		cls = classes.find_containing(words[1])
		if cls is None:
			continue
		prob = cls.get_probability(words[1])
		cls.add(words[0], prob)
	elif classes.find_containing(words[1]) is None:
		prob = cls.get_probability(words[0])
		cls.add(words[1], prob)
	else:
		continue

classes.write(sys.stdout)
