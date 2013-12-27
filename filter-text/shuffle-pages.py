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
parser.add_argument('--in-memory', action='store_true', default=False, help='load the entire data set into memory')
args = parser.parse_args()

uris = set()
pages = dict()
for input_file in args.input:
	for page in read_page_pointers(input_file):
		uri = page.uri()
		uris.add(uri)
		if uri in pages:
			pages[uri].add_pages(page.pointers())
		else:
			pages[uri] = page

num_pages = len(uris)
sys.stderr.write("%i pages in the input files.\n" % num_pages)

ordered_uris = list(uris)

previous_progress = -1
while len(ordered_uris) > 0:
	index = random.randint(0, len(ordered_uris) - 1)
	uri = ordered_uris[index]
	del ordered_uris[index]
	progress = int((num_pages - len(ordered_uris)) * 100 / num_pages)
	if progress > previous_progress:
		sys.stderr.write("%i %% done.\n" % progress)
		previous_progress = progress

	args.output.write(pages[uri].header())
	args.output.write(pages[uri].content())
	args.output.flush()
