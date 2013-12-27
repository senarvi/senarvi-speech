#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Selects text pages based on a list of page identifiers.
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
parser.add_argument('list', type=TextFileType('r'), help='a file containing a page identifier on each line')
parser.add_argument('--output', type=TextFileType('w'), default='-', help='output filtered text pages')
parser.add_argument('--pages', type=TextFileType('r'), default='-', help='input text pages')
parser.add_argument('--write-headers', action='store_true', default=False, help='write also page headers so that the pages can be further filtered')
args = parser.parse_args()

select_uris = set(args.list.read().splitlines())
args.list.close()

include = False
for line in args.pages:
	if line.startswith("###### "):
		uri = line[7:].rstrip()
		include = uri in select_uris
		if args.write_headers and include:
			args.output.write(line)
	elif include:
		args.output.write(line)
