#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Interpolates LM probabilities in n-best list with new LM probabilities.
#
# Takes as input an n-best list, which is in SRILM format, except that an
# additional first column contains the utterance ID. The new LM probabilities
# are read from another file that contains one log probability per line. Writes
# a new n-best list to standard output, in the same format, with the LM scores
# interpolated using the following formula:
#
#   log(exp(score1 * scale1) * (1-lambda) + exp(score2 * scale2) * lambda))
#
# All the log probabilities are base 10.
#
# Author: Seppo Enarvi
# http://users.marjaniemi.com/seppo/

import argparse
import sys
from decimal import *
from filetypes import TextFileType

parser = argparse.ArgumentParser()
parser.add_argument(
    'nbestlist', type=TextFileType('r'),
    help='n-best list in SRILM format with each line prefixed by utterance ID')
parser.add_argument(
    'newscores', type=TextFileType('r'),
    help='a file containing a new LM score for each hypothesis in the n-best list')
parser.add_argument(
    '--scale1', metavar='SCALE', type=float, default=1.0,
    help='scale old LM probabilities by this factor')
parser.add_argument(
    '--scale2', metavar='SCALE', type=float, default=1.0,
    help='scale new LM probabilities by this factor')
parser.add_argument(
    '--lambda', metavar='LAMBDA', dest='lambda2', type=float, default=0.5,
    help='interpolation weight to apply to the new probabilities')
args = parser.parse_args()

getcontext().prec = 6

scale1 = Decimal(args.scale1)
scale2 = Decimal(args.scale2)
lambda2 = Decimal(args.lambda2)
lambda1 = Decimal(1) - lambda2

for nbest_line, newscores_line in zip(args.nbestlist, args.newscores):
    fields = nbest_line.split()
    id = fields[0]
    ascore = float(fields[1])
    lscore1 = Decimal(fields[2])
    nwords = int(fields[3])
    words = fields[4:]
    if nwords != len(words):
        sys.stderr.write(
            "Warning: nwords field does not match the number of words in "
            "n-best list.\n")

    lscore2 = Decimal(newscores_line)

    lscore1 *= scale1
    lprob1 = Decimal(10) ** lscore1
    lprob1 *= lambda1

    lscore2 *= scale2
    lprob2 = Decimal(10) ** lscore2
    lprob2 *= lambda2

    lprob = lprob1 + lprob2
    lscore = lprob.log10()

    sys.stdout.write(id + " ")
    sys.stdout.write(str(ascore) + " ")
    sys.stdout.write(str(lscore) + " ")
    sys.stdout.write(str(nwords) + " ")
    sys.stdout.write(" ".join(words) + "\n")
