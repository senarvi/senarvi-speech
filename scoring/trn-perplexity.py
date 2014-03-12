#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Computes the perplexity of a language model on a transcript file in
# sclite "trn" format. Each line of the transcript file must contain a
# word sequence follow by an utterance ID enclosed in parenthesis.
# Alternations can be used in the word sequence, e.g.
#
#   i've { um / uh / @ } as far as i'm concerned
#
# The "@" represents the possibility that the word is omitted. Language
# model probability is computed as the maximum of that of the possible
# alternatives.
#
# Author: Seppo Enarvi
# http://users.marjaniemi.com/seppo/

import argparse
from filetypes import TextFileType
from ArpaLM import ArpaLM
from transcripts import Transcripts

def prepend_alternatives(head, token, max_length):
	result = list()
	if type(token) is list:
		for head_alt in head:
			for tail_alt in token:
				if tail_alt == ['@']:
					result.append(head_alt)
				else:
					new_alt = tail_alt + head_alt
					if len(new_alt) > max_length:
						new_alt = new_alt[len(new_alt)-max_length:]
					result.append(new_alt)
	else:
		for head_alt in head:
			new_alt = [token] + head_alt
			if len(new_alt) > max_length:
				new_alt = new_alt[len(new_alt)-max_length:]
			result.append(new_alt)
	return result

parser = argparse.ArgumentParser()
parser.add_argument('lm', type=TextFileType('r'), help='arpa language model file')
parser.add_argument('trn', type=TextFileType('r'), help='transcript file')
args = parser.parse_args()

lm = ArpaLM(args.lm)
args.lm.close()

trn = Transcripts()
trn.read_trn(args.trn)
args.trn.close()

lm_order = lm.get_size()
print('lm_order:', lm_order)

logprob_sum = 0
num_words = 0
num_oov_words = 0
for utterance_id, transcript in trn:
	for last_index in range(len(transcript)):
		# Enumerate all the alternative paths through the transcript.
		# Add a dummy trailing '' and remove it in the end.
		alternatives = [['']]
		for index in reversed(range(last_index + 1)):
			alternatives = prepend_alternatives(alternatives, transcript[index], lm_order + 1)
		alternatives = [x[:len(x)-1] for x in alternatives]

		# Find out the maximum logprob over the alternatives.
		max_logprob = None
		for alt in alternatives:
			try:
				logprob = lm.prob(*reversed(alt))
				if (max_logprob is None) or (logprob > max_logprob):
					max_logprob = logprob
			except ArpaLM.OOVError:
				pass

		# Update the sum of the maximum logprobs.
		num_words += 1
		if max_logprob is None:
			num_oov_words += 1
		else:
			logprob_sum += max_logprob

print('logprob_sum:', logprob_sum)
print('num_words:', num_words)
print('num_oov_words:', num_oov_words)

cross_entropy = -logprob_sum / num_words
print('cross_entropy:', cross_entropy)
