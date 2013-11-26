#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Splits a pages file into chunks from page boundaries.
#
# Author: Seppo Enarvi
# http://users.marjaniemi.com/seppo/

import argparse
import sys
from collections import OrderedDict
from filetypes import TextFileType


parser = argparse.ArgumentParser()
parser.add_argument('pages', type=TextFileType('r'), nargs='?', default='-', help='input pages file')
parser.add_argument('-b', '--bytes', type=int, default=536870912, help='target chunk size in bytes')
parser.add_argument('--prefix', type=str, default='x', help='output file prefix')
args = parser.parse_args()

chunk_number = 1
output_file = open(args.prefix + '.1', 'w', encoding='utf-8')
current_bytes = 0
for line in args.pages:
	if line.startswith("###### "):
		uri = line[7:].rstrip()
		if uri.find('#') == -1:
			if current_bytes > args.bytes:
				output_file.close()
				chunk_number += 1
				output_file = open(args.prefix + '.' + str(chunk_number), 'w', encoding='utf-8')
				current_bytes = 0
	output_file.write(line)
	current_bytes += len(line.encode('utf-8'))
output_file.close()
