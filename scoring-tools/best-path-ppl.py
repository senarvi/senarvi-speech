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
# model probability is computed as the maximum of that of the
# alternative paths through the transcript.
#
# Author: Seppo Enarvi
# http://users.marjaniemi.com/seppo/

import argparse
import math
from copy import copy, deepcopy
from filetypes import TextFileType
from ArpaLM import ArpaLM
from transcripts import Transcripts

class Path:
	def __init__(self):
		self.__history = ['<s>']
		self.__logprob = 0

	def __repr__(self):
		return str(self.logprob()) + ' ' + ' '.join(self.history())

	def history(self):
		return self.__history

	def logprob(self):
		return self.__logprob

	def append(self, word, lm):
		self.__history.append(word)
		word_logprob = lm.prob(*reversed(self.history()))
		if word_logprob == float('-inf'):
			raise ArpaLM.OOVError(word)
		self.__logprob += word_logprob

class AlternativePaths:
	def __init__(self, lm):
		self.lm = lm
		self.alternatives = [Path()]

	def __repr__(self):
		return '\n'.join([str(x) for x in self.alternatives])

	# Appends a word to all alternatives.
	def append(self, word):
		for i in range(len(self.alternatives) - 1, -1, -1):
			try:
				self.alternatives[i].append(word, lm)
			except ArpaLM.OOVError:
				del self.alternatives[i]

	# Appends each word sequence to all alternatives.
	# '@' represents the NULL word.
	def extend(self, seqs):
		# This way we don't have multiple copies of old alternatives
		# even if there are multiple @ (NULL) words. We still need to
		# copy self.alternatives, though. Otherwise extending
		# new_alternatives will extend self.alternatives as well.
		if ['@'] in seqs:
			new_alternatives = copy(self.alternatives)
		else:
			new_alternatives = []

		for seq in seqs:
			if seq == ['@']:
				continue
			for alt in self.alternatives:
				try:
					new_alt = deepcopy(alt)
					for word in seq:
						new_alt.append(word, lm)
					new_alternatives.append(new_alt)
				except ArpaLM.OOVError:
					pass

		self.alternatives = new_alternatives

	# Prunes worst alternatives, leaving a maximum of max_alternatives.
	def prune(self, max_alternatives):
		if len(self.alternatives) > max_alternatives:
			self.alternatives.sort(key=lambda x: x.logprob(), reverse=True)
			self.alternatives = self.alternatives[:max_alternatives]

	def size(self):
		return len(self.alternatives)

	def best(self):
		if len(self.alternatives) > 0:
			return max(self.alternatives, key=lambda x: x.logprob())
		else:
			return None

parser = argparse.ArgumentParser()
parser.add_argument('lm', type=TextFileType('r'), help='arpa language model file')
parser.add_argument('trn', type=TextFileType('r'), help='transcript file')
parser.add_argument('--max-alternatives', type=int, default=None, help='maximum number of best alternatives to keep in memory at a time')
args = parser.parse_args()

lm = ArpaLM(args.lm)
args.lm.close()

trn = Transcripts()
trn.read_trn(args.trn)
args.trn.close()

logprob_sum = 0
num_words = 0
num_rejected_sentences = 0
for utterance_id, transcript in trn:
	alternatives = AlternativePaths(lm)
	if (len(transcript) >= 2) and (transcript[0] == '<s>') and (transcript[-1] == '</s>'):
		transcript = transcript[1:-1]
	for token in transcript:
		if type(token) is list:
			alternatives.extend(token)
		else:
			alternatives.append(token)
		if args.max_alternatives is not None:
			alternatives.prune(args.max_alternatives)
	alternatives.append('</s>')

	best_alternative = alternatives.best()
	if best_alternative is not None:
		# When using subword models, the transcripts always contain a word boundary
		# after the initial <s> and before the final </s>. There may be two
		# consecutive word boundaries, at least if the transcript is empty. We
		# remove first consecutive word boundary symbols.
		hist = best_alternative.history()
		hist = [x for i, x in enumerate(hist) if hist[i:i+2] != ['<w>', '<w>']]

		# Now the number of word boundaries equals to the number of words, omitting
		# the initial sentence start, or in case of a word model, the number of
		# tokens minus one.
		num_word_boundaries = hist.count('<w>')
		if num_word_boundaries >= 1:
			num_words += num_word_boundaries
		else:
			num_words += len(hist) - 1

		logprob_sum += best_alternative.logprob()
		print(best_alternative, '(' + str(utterance_id) + ')')
	else:
		num_rejected_sentences += 1

logprob_sum_base2 = logprob_sum / math.log(2)
logprob_sum_base10 = logprob_sum / math.log(10)

print('num_words:', num_words)
print('num_rejected_sentences:', num_rejected_sentences)
print('logprob_sum:', logprob_sum)
print('logprob_sum_base2:', logprob_sum_base2)
print('logprob_sum_base10:', logprob_sum_base10)

if num_words > 0:
	cross_entropy = -logprob_sum / num_words
	cross_entropy_base2 = -logprob_sum_base2 / num_words
	cross_entropy_base10 = -logprob_sum_base10 / num_words

	perplexity = math.exp(cross_entropy)
	perplexity_base2 = math.pow(2, cross_entropy)
	perplexity_base10 = math.pow(10, cross_entropy)

	print('cross_entropy:', cross_entropy)
	print('cross_entropy_base2:', cross_entropy_base2)
	print('cross_entropy_base10:', cross_entropy_base10)

	print('perplexity:', perplexity)
	print('perplexity_base2:', perplexity_base2)
	print('perplexity_base10:', perplexity_base10)

