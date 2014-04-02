#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Splits a pages file into chunks from page boundaries.
# Supports overlapping chunks (offset != chunk size).
#
# Author: Seppo Enarvi
# http://users.marjaniemi.com/seppo/

import argparse
import sys
from collections import OrderedDict
from filetypes import TextFileType

class Chunk:
	def __init__(self, number, prefix):
		self.file = open(prefix + '.' + str(number), 'w', encoding='utf-8')
		self.bytes = 0

	def __del__(self):
		self.file.close()

	def write(self, text):
		self.file.write(text)
		self.bytes += len(line.encode('utf-8'))


parser = argparse.ArgumentParser()
parser.add_argument('pages', type=TextFileType('r'), nargs='?', default='-', help='input pages file')
parser.add_argument('-b', '--bytes', type=int, default=536870912, help='target chunk size in bytes')
parser.add_argument('-o', '--offset', type=int, default=None, help='target offset between chunks in bytes')
parser.add_argument('--prefix', type=str, default='x', help='output file prefix')
args = parser.parse_args()

if args.offset is None:
	args.offset = args.bytes

chunk_number = 1
chunks = [Chunk(chunk_number, args.prefix)]
chunk_number += 1

current_offset = 0
for line in args.pages:
	if line.startswith("###### "):
		uri = line[7:].rstrip()
		if uri.find('#') == -1:
			if current_offset > args.offset:
				chunks.append(Chunk(chunk_number, args.prefix))
				chunk_number += 1
				current_offset = 0
			for index, chunk in enumerate(chunks):
				if chunk.bytes > args.bytes:
					del chunks[index]

	for chunk in chunks:
		chunk.write(line)
	current_offset += len(line.encode('utf-8'))
