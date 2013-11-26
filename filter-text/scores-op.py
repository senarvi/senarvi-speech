#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Performs arithmetic operations on text segment scores. Can be used to
# take the cross-entropy difference, as in Moore and Lewis (2010), given
# two score files that contain the perplexities of an in-domain and a
# non-domain-specific language model:
#
# scores-op.py sub <(scores-op.py log10 id.scores) <(scores-op.py log10 nds.scores)
#
# Author: Seppo Enarvi
# http://users.marjaniemi.com/seppo/

import argparse
import sys
import math
import operator
from pages import read_scores
from filetypes import TextFileType


parser = argparse.ArgumentParser()
parser.add_argument('operation', type=str, help='arithmetic operation (e.g. sub, log10)')
parser.add_argument('input', type=TextFileType('r'), nargs='+', help='input scores file')
parser.add_argument('--output', type=TextFileType('w'), default='-', help='output scores file')
args = parser.parse_args()

if hasattr(operator, args.operation):
	method = getattr(operator, args.operation)
elif hasattr(math, args.operation):
	method = getattr(math, args.operation)
else:
	sys.stderr.write("Unknown operation '%s'.\n" % args.operation)
	sys.exit(2)

if len(args.input) == 1:
	scores = read_scores(args.input[0])
	print(len(scores))
	for uri, score in scores.items():
		result = method(score)
		args.output.write("###### %s\n%f\n" % (uri, result))
		args.output.write("%f\n" % score)
elif len(args.input) == 2:
	scores1 = read_scores(args.input[0])
	scores2 = read_scores(args.input[1])
	for uri, score1 in scores1.items():
		score2 = scores2[uri]
		result = method(score1, score2)
		args.output.write("###### %s\n%f\n" % (uri, result))
		args.output.write("%f, %f\n" % (score1, score2))
else:
	sys.stderr.write("Expecting at most two score files.\n")
	sys.exit(2)
