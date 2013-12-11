#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Executes a subprocess on every page. Sends either the current page, or
# everything but the current page, to the child's standard input. The subprocess
# should score the text based on perplexity or similar measure.
#
# Author: Seppo Enarvi
# http://users.marjaniemi.com/seppo/

import argparse
import sys
import io
import subprocess
from pages import *
from filetypes import TextFileType

parser = argparse.ArgumentParser()
parser.add_argument('command', type=str, help='a command that scores text')
parser.add_argument('input', type=TextFileType('r'), nargs='+', help='input text page files')
parser.add_argument('--in-memory', action='store_true', default=False, help='load the entire data set into memory')
parser.add_argument('--unit', type=str, default='each', help='send one page at a time ("each"), everything but one page at a time ("exclude"), or all at once ("all")')
parser.add_argument('--scores', type=str, default='-', help='output scores file')
parser.add_argument('--merge-fragments', action='store_true', default=False, help='merge pages whose URI only differs after fragment identifier')
parser.add_argument('-B', '--batch', type=int, dest='num_batches', default=1, help='number of batches to split the job into')
parser.add_argument('-I', '--bindex', type=int, dest='batch_index', default=1, help='index of this batch, starting from 1')
args = parser.parse_args()

if args.batch_index > args.num_batches:
	sys.stderr.write("Batch index has to be smaller than or equal to the number of batches.\n")
	sys.exit(2)
if args.batch_index < 1:
	sys.stderr.write("Batch indices start from 1.\n")
	sys.exit(2)

existing_uris = set()
if args.scores == '-':
	scores_file = TextFileType('w')(args.scores)
else:
	try:
		scores_file = TextFileType('r')(args.scores)
		for line in scores_file:
			if line.startswith('###### '):
				existing_uris.add(line[7:].strip())
		scores_file.close()
		scores_file = TextFileType('a')(args.scores)
		scores_file = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
	except argparse.ArgumentTypeError:
		scores_file = TextFileType('w')(args.scores)

# Send pages according to --unit.
if args.unit == "all":
	process = subprocess.Popen([args.command], stdin=subprocess.PIPE, stdout=subprocess.PIPE);
	output_file = io.TextIOWrapper(process.stdin, 'utf-8')
	for input_file in args.input:
		write_all_content(input_file, output_file)
	process.stdin.close()
	score = float(process.stdout.readline())
	scores_file.write(str(score))
	
else:
	if args.unit == "each":
		include_match = True
	elif args.unit == "exclude":
		include_match = False
	else:
		sys.stderr.write("Unknown unit: " + args.unit + "\n")
		sys.exit(2)

	all_uris = set()
	pages = dict()
	for input_file in args.input:
		for page in read_pages(input_file, not args.merge_fragments):
			uri = page.uri()
			all_uris.add(uri)
			if uri in pages:
				pages[uri] += page.content()
			else:
				pages[uri] = page.content()

	batch_uris = sorted(all_uris)[args.batch_index-1::args.num_batches]
	previous_progress = -1
	for index, uri in enumerate(batch_uris):
		if uri in existing_uris:
			continue
		progress = int(index * 100 / len(batch_uris))
		if progress > previous_progress:
			sys.stderr.write("Batch %i/%i: %i %% done.\n" % (args.batch_index, args.num_batches, progress))
			previous_progress = progress
		sys.stderr.flush()
		process = subprocess.Popen([args.command], stdin=subprocess.PIPE, stdout=subprocess.PIPE);
		output_file = io.TextIOWrapper(process.stdin, 'utf-8')
		if args.in_memory:
			if include_match:
				output_file.write(pages[uri])
			else:
				for uri2 in all_uris:
					if uri2 != uri:
						output_file.write(pages[uri2])
		else:
			for input_file in args.input:
				write_matching_content(input_file, output_file, uri, args.merge_fragments, include_match)
		output_file.close()
		process.stdin.close()
		score_str = process.stdout.readline()
		try:
			score = float(score_str)
		except ValueError:
			sys.stderr.write("Invalid score '%s' for page %s.\n" % (score_str, uri))
			sys.exit(3)
		scores_file.write("###### %s\n%f\n" % (uri, score))
		scores_file.flush()

	sys.stderr.write("Batch %i/%i finished.\n" % (args.batch_index, args.num_batches))
