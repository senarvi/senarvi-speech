#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Filters text pages based on a scores file and a threshold.
#
# Author: Seppo Enarvi
# http://users.marjaniemi.com/seppo/

import argparse
import sys
import io
import tempfile
import subprocess
import re
from perplexity import *
from pages import *
from filetypes import TextFileType


parser = argparse.ArgumentParser()
parser.add_argument('scores', type=TextFileType('r'), help='input scores file')
parser.add_argument('--pages', type=TextFileType('r'), default='-', help='input text pages')
parser.add_argument('--output', type=TextFileType('w'), default='-', help='output filtered text pages')
parser.add_argument('--merge-fragments', action='store_true', default=False, help='merge pages whose URI only differs after fragment identifier')
parser.add_argument('--min-score', type=float, default=None, help='filter out pages with score below this threshold')
parser.add_argument('--max-score', type=float, default=None, help='filter out pages with score above this threshold')
parser.add_argument('--write-headers', action='store_true', default=False, help='write also page headers so that the pages can be further filtered')
args = parser.parse_args()

scores = read_scores(args.scores)
args.scores.close()

try:
	min_score = args.min_score
	max_score = args.max_score
	include = False
	for line in args.pages:
		if line.startswith("###### "):
			uri = line[7:].rstrip()
			include = True
			if min_score is not None:
				if uri in scores and scores[uri] < min_score:
					include = False
			if max_score is not None:
				if uri in scores and scores[uri] > max_score:
					include = False
			if args.write_headers and include:
				args.output.write(line)
		elif include:
			args.output.write(line)
except subprocess.CalledProcessError as e:
	sys.stderr.write("Command '%s' failed with exit status %i.\n" % (' '.join(e.cmd), e.returncode))
	if e.output is not None:
		sys.stderr.write("Program output:\n")
		sys.stderr.write(e.output.decode('utf-8'))

