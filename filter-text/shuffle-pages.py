#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Randomly reorders text segments. Should be done before passing text segments
# to re-min-select.py, because the minimum relative error algorithm is greedy.
#
# Author: Seppo Enarvi
# http://users.marjaniemi.com/seppo/

import argparse
import random
from pages import *
from filetypes import TextFileType

parser = argparse.ArgumentParser()
parser.add_argument('input', type=TextFileType('r'), nargs='+', help='input text page files')
parser.add_argument('--output', type=TextFileType('w'), default='-', help='output file for reordered text pages')
args = parser.parse_args()

pages = dict()
for input_file in args.input:
	sys.stderr.write("Reading input file %s.\n" % input_file.name)
	sys.stderr.flush()
	for page in read_page_pointers(input_file):
		uri = page.uri()
		if uri in pages:
			pages[uri].add_pages(page.pointers())
		else:
			pages[uri] = page

num_pages = len(pages)
sys.stderr.write("%i pages in the input files.\n" % num_pages)
sys.stderr.flush()

ordered_pages = list(pages.values())
random.shuffle(ordered_pages)
sys.stderr.write("Random permutation generated.\n")
sys.stderr.flush()

previous_progress = -1
num_written_pages = 0
for page in ordered_pages:
	args.output.write(page.header())
	args.output.write(page.content())
	args.output.flush()

	num_written_pages += 1
	progress = int(num_written_pages * 100 / num_pages)
	if progress > previous_progress:
		sys.stderr.write("%i %% done.\n" % progress)
		sys.stderr.flush()
		previous_progress = progress
