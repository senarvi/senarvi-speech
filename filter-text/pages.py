#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# A module for reading pages and scores files.
#
# Author: Seppo Enarvi
# http://users.marjaniemi.com/seppo/

import sys
import string

class Page:
	def __init__(self, uri=None, content=''):
		self.__uri = uri
		self.__content = content
	
	def empty(self):
		if self.__uri is None:
			return True
		return all(ch in string.whitespace for ch in self.__content)
	
	def uri(self):
		return self.__uri
	
	def header(self):
		return '###### ' + self.__uri + '\n'
	
	def content(self):
		return self.__content.rstrip() + '\n'
	
	def add_content(self, x):
		self.__content += x

# Reads all the pages for given batch.
def read_pages(file, fragments=True):
	page = Page()
	for line in file:
		if line.startswith('###### '):
			if not page.empty():
				yield page
			uri = line[7:].rstrip()
			if not fragments:
				end = uri.find('#')
				if end != -1:
					uri = uri[:end]
			page = Page(uri, '')
		else:
			page.add_content(line)
	if not page.empty():
		yield page

# Reads all the scores into a dictionary.
def read_scores(file):
	scores = {}
	uri = None
	score = None
	for line in file:
		if line.startswith("###### "):
			if uri is not None and score is not None:
				scores[uri] = score
			uri = line[7:].rstrip()
			score = None
		else:
			try:
				score = float(line)
			except ValueError:
				sys.stderr.write("Invalid score: " + line + "\n")
				sys.stderr.write("URI: " + uri + "\n")
				sys.exit(1)
	if uri is not None and score is not None:
		scores[uri] = score
	return scores

# Writes content from all input pages to output file.
def write_all_content(input_file, output_file):
	for line in input_file:
		if not line.startswith("###### "):
			output_file.write(line)

# Writes either matching page content (include_match = True), or every other
# page content (include_match = False).
def write_matching_content(input_file, output_file, match_uri, match_fragments, include_match=True):
	match = False
	for line in input_file:
		if line.startswith("###### "):
			uri = line[7:].rstrip()
			match = False
			if uri == match_uri:
				match = True
			elif match_fragments:
				end = uri.find('#')
				if (end != -1) and (uri[:end] == match_uri):
					match = True
		elif include_match:
			if match:
				output_file.write(line)
		else:
			if not match:
				output_file.write(line)
