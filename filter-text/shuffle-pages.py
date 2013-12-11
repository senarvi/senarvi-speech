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

uris = set()
pages = dict()
for input_file in args.input:
	for page in read_pages(input_file):
		uri = page.uri()
		uris.add(uri)
		if uri in pages:
			pages[uri].add_content(page.content())
		else:
			pages[uri] = page
sys.stderr.write("%i pages in the input files.\n" % len(uris))

ordered_uris = list(uris)
random.shuffle(ordered_uris)

for uri in ordered_uris:
	args.output.write(pages[uri].header())
	args.output.write(pages[uri].content())
