#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Computes the optimal mixture (in terms of devel text perplexity) of language
# models, and creates an interpolated language model using SRILM.

import argparse
import sys
import tempfile
import subprocess
import re
from filetypes import TextFileType

parser = argparse.ArgumentParser()
parser.add_argument('input', type=str, nargs='+', help='two or more input models')
parser.add_argument('--output', type=str, default='-', help='output model path (default is stdout)')
parser.add_argument('--write-weights', type=str, default=None, help='write the optimized weights to this file, separated by space')
parser.add_argument('--order', type=int, default=3, help='output n-gram model order (default is 3)')
parser.add_argument('--opt-perp', type=str, dest='tuning_text', default=None, help='a development text for tuning interpolation weights')
parser.add_argument('--ngram-cmd', type=str, default='ngram', help='SRILM ngram executable (default is "ngram")')
args = parser.parse_args()

num_components = len(args.input)
if num_components < 2:
	sys.stderr.write("Expecting two or more input models.\n")
	sys.exit(1)

equal_lambda = 1.0 / num_components

if args.tuning_text is not None:
	ppl_files = []
	for model_path in args.input:
		ppl_files.append(tempfile.NamedTemporaryFile())
		command = [args.ngram_cmd,
		           '-order', str(args.order),
		           '-lm', model_path,
		           '-ppl', args.tuning_text,
		           '-debug', '2']
		print(' '.join(command))
		ppl_files[-1].write(subprocess.check_output(command))
		ppl_files[-1].flush()
	lambda_arg = 'lambda=' + ' '.join([str(equal_lambda)] * num_components)
	command = ['compute-best-mix', lambda_arg ]
	command.extend([x.name for x in ppl_files])
	print(' '.join(command))
	output = subprocess.check_output(command).decode('utf-8')
	matches = re.search(r'best lambda \(([0-9.e\- ]+)\)', output)
	if not matches:
		sys.stderr.write("Couldn't parse compute-best-mix output.\n")
		sys.stderr.write("Output was:\n")
		sys.stderr.write(output)
		sys.exit(1)
	lambdas = matches.group(1).split(' ')
else:
	lambdas = [str(equal_lambda)] * num_components

if args.write_weights:

command = [args.ngram_cmd,
		'-order', str(args.order),
		'-write-lm', args.output,
		'-lm', args.input[0],
		'-lambda', lambdas[0],
		'-mix-lm', args.input[1]]
for i in range(2, num_components):
	command.append('-mix-lm' + str(i))
	command.append(args.input[i])
	command.append('-mix-lambda' + str(i))
	command.append(lambdas[i])
print(' '.join(command))
subprocess.check_call(command)
