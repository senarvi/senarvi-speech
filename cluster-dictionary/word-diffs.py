#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Reads a list of word pairs, one pair per line, and shows the
# edit operations needed to transform one word into the other.

import argparse
import sys
from filetypes import TextFileType
from editpartitioning import EditPartitioning
from finnishreductions import validate

parser = argparse.ArgumentParser()
parser.add_argument('wordpairs', type=TextFileType('r'), help='file containing word pairs, one per line')
parser.add_argument('--validate-finnish', action='store_true', default=False, help='prints only pairs that are not conversational Finnish reductions')
args = parser.parse_args()

for line in args.wordpairs:
	line = line.strip()
	if len(line) == 0:
		continue
	words = line.split()
	if len(words) != 2:
		sys.stderr.write("Invalid word pair: " + line + "\n")
		continue
	edits = EditPartitioning(words[1], words[0])
	edits.clean()
	if args.validate_finnish:
		if validate(edits.partitions):
			print(edits, "\t\tVALID")
		else:
			print(edits, "\t\tUNRECOGNIZED")
	else:
		print(edits)
	sys.stdout.flush()
