#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Removes duplicate text segments.
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

seen_pages = set()
for input_file in args.input:
	for page in read_pages(input_file):
		if not page.content() in seen_pages:
			seen_pages.add(page.content())
			args.output.write(page.header())
			args.output.write(page.content())
			args.output.flush()
