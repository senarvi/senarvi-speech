#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re

def trn_transcript(utterance_id, transcript):
	words = []
	for token in transcript:
		words.append(trn_alternation(token))
	words.append('(' + utterance_id + ')')
	return ' '.join(words)

def trn_alternation(alternation):
	words = []
	if type(alternation) is list:
		words.append('{')
		words.append(' / '.join([' '.join(x) for x in alternation]))
		words.append('}')
	else:
		words.append(alternation)
	return ' '.join(words)

class Transcripts:
	'''
	A transcript database.
	'''

	def __init__(self):
		self.__transcripts = dict()

	def __iter__(self):
		for utterance_id, transcript in self.__transcripts.items():
			yield utterance_id, transcript
	
	def read_trn(self, input_file):
		for line in input_file:
			utterance_end = line.index('(')
			id_start = utterance_end + 1
			id_end = line.index(')', id_start)
			utterance = line[:utterance_end].strip()
			utterance_id = line[id_start:id_end].strip()
			self.set_utterance(utterance_id, utterance)
	
	def write_trn(self, output_file):
		for utterance_id, transcript in self.__transcripts.items():
			line = trn_transcript(utterance_id, transcript)
			output_file.write(line.encode('utf-8') + '\n')
	
	def set_utterance(self, utterance_id, utterance):
		transcript = []
		pos = 0
		while pos < len(utterance):
			alt_pos = utterance.find('{', pos)
			if alt_pos == -1:
				transcript.extend(utterance[pos:].split())
				break
			transcript.extend(utterance[pos:alt_pos].split())
			alt_pos += 1
			alt_end = utterance.find('}', alt_pos)
			alternation = utterance[alt_pos:alt_end].split('/')
			alternation = [x.split() for x in alternation]
			transcript.append(alternation)
			pos = alt_end + 1
		self.__transcripts[utterance_id] = transcript
	
	def set_transcript(self, utterance_id, transcript):
		self.__transcripts[utterance_id] = transcript
