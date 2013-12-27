#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Implementation of the relative entropy minimization based data selection
# algorithm described in [Sethy et al. 2009]. Supports only unigram models.
#
# Expects as an input the non-domain-specific text pages, a unigram in-domain
# language model, and a random sample from the non-domain-specific text that is
# the same size as the data that was used to estimate the in-domain language
# model.
#
# Writes the identifires of the selected text segments to standard output. 
#
# Author: Seppo Enarvi
# http://users.marjaniemi.com/seppo/

import argparse
import re
import math
from pages import *
from filetypes import TextFileType

LN10 = 2.30258509299404568402

def next_nonempty_line(file):
	for line in file:
		line = line.strip()
		if not line:
			continue
		return line

def read_unigram_lm(lm_file):
	line = next_nonempty_line(lm_file)
	if line != '\\data\\':
		raise Exception('read_unigram_lm: "%s" where "\\data\\" expected.' % line)
	
	line = next_nonempty_line(lm_file)
	pattern = re.compile('ngram\s+1\s*=\s*(\d+)')
	match = pattern.match(line)
	if match is None:
		raise Exception('read_unigram_lm: "%s" where "ngram 1=..." expected.' % line)
	num_entries = int(match.group(1))
	
	line = next_nonempty_line(lm_file)
	if line != '\\1-grams:':
		raise Exception('read_unigram_lm: "%s" where "\\1-grams:" expected.' % line)
	
	line = next_nonempty_line(lm_file)
	result = dict()
	while line != '\\end\\':
		elements = line.split()
		if len(elements) != 2:
			raise Exception('read_unigram_lm: "%s" where a probability and a word expected.' % line)
		logprob = float(elements[0]) * LN10
		word = elements[1]
		result[word] = logprob
		line = next_nonempty_line(lm_file)

	if len(result) != num_entries:
		sys.stderr.write('read_unigram_lm: %i entries read, while %i entries expected.\n' % (len(result), num_entries))
	return result

def word_counts(text, vocab=None):
	result = dict()
	if vocab is not None:
		for word in vocab:
			result[word] = 1
	
	oov_tokens = 0
	for word in text.split():
		if word in result:
			result[word] += 1
		elif vocab is None:
			result[word] = 1
		else:
			oov_tokens += 1

	if oov_tokens > 0:
		sys.stderr.write('word_counts: %i word tokens not in vocabulary.\n' % oov_tokens)
	
	return result

def logsum(x, y):
	return y + math.log(1 + math.exp(x - y))

def divergence(counts, id_model, alpha):
	logalpha = math.log(alpha)
	beta = 1 - alpha
	if beta > 0:
		logbeta = math.log(beta)
	else:
		logbeta = None
	
	result = 0
	total_count = sum(counts.values())
	for word in id_model.keys():
#		id_prob = math.exp(id_model[word])
#		ml_prob = float(counts[word]) / total_count
#		ratio = id_prob / ((beta * id_prob) + (alpha * ml_prob))
#		result += id_prob * math.log(ratio)

		id_logprob = id_model[word]
		ml_logprob = math.log(float(counts[word]) / total_count)
		if logbeta is None:
			logratio = id_logprob - ml_logprob
		else:
			logratio = id_logprob - logsum(logbeta + id_logprob, logalpha + ml_logprob)
		result += math.exp(id_logprob) * logratio
	
	return result

def divergence_increment(selected_counts, page_counts, id_model, alpha):
	logalpha = math.log(alpha)
	beta = 1 - alpha
	if beta > 0:
		logbeta = math.log(beta)
	else:
		logbeta = None
	
	selected_total_count = sum(selected_counts.values())
	page_total_count = sum(page_counts.values())
	new_total_count = selected_total_count + page_total_count
	
	selected_total_logcount = math.log(selected_total_count)
	new_total_logcount = math.log(new_total_count)

	result = math.log(new_total_count / selected_total_count)
	logresult = math.log(new_total_count / selected_total_count)
	
	oov_words = 0
	for word in page_counts.keys():
		if not word in selected_counts:
			oov_words += 1
			continue
		
#		id_prob = math.exp(id_model[word])
#		old_count = selected_counts[word]
#		new_count = old_count + page_counts[word]
#		ratio = (beta * id_prob * new_total_count) + (alpha * new_count)
#		ratio /= (beta * id_prob * selected_total_count) + (alpha * old_count)
#		result -= id_prob * math.log(ratio)

		id_logprob = id_model[word]
		old_logcount = math.log(selected_counts[word])
		new_logcount = math.log(selected_counts[word] + page_counts[word])
		if logbeta is None:
			logratio = new_logcount - old_logcount
		else:
			logratio = logsum(logbeta + id_logprob + new_total_logcount, logalpha + new_logcount)
			logratio -= logsum(logbeta + id_logprob + selected_total_logcount, logalpha + old_logcount)
		result -= math.exp(id_logprob) * logratio

	if oov_words > 0:
		sys.stderr.write('divergence_increment: %i words not in vocabulary.\n' % oov_words)
	
	return result

def select_text(pages_file, selected_counts, id_model, alpha, limit=None):
	div = divergence(selected_counts, id_model, alpha)
	sys.stderr.write('divergence: %f\n' % div)
	if limit is not None:
		sys.stderr.write('Selecting %i words.\n' % limit)

	oov_words = 0
	result = ''
	result_length = 0
	message_count = 0
	for page in read_pages(pages_file):
		page_counts = word_counts(page.content())
		div_inc = divergence_increment(selected_counts, page_counts, id_model, alpha)
		if div_inc < 0:
			div += div_inc
			
			for word in page_counts:
				if word in selected_counts:
					selected_counts[word] += page_counts[word]
					result_length += page_counts[word]
				else:
					oov_words += 1

			sys.stdout.write(page.uri() + '\n')
			
			if message_count < result_length / 100000:
				sys.stderr.write('%i words selected, divergence: %f\n' % (result_length, div))
				message_count += 1
			
			if limit is not None:
				result += page.content()
				if result_length > limit:
					break
	
	if oov_words > 0:
		sys.stderr.write('select_text: %i words not in vocabulary.\n' % oov_words)
	
	sys.stderr.write('%i words selected, divergence: %f\n' % (result_length, div))
	return result

parser = argparse.ArgumentParser()
parser.add_argument('pages', type=TextFileType('r'), help='input text pages')
parser.add_argument('ndssample', type=TextFileType('r'), help='a random sample from the non-domain-specific data')
parser.add_argument('idmodel', type=TextFileType('r'), help='unigram in-domain language model')
parser.add_argument('--alpha', type=float, default=1, help='the skew divergence parameter denoting the smoothing influence')
args = parser.parse_args()

# Read in-domain unigram model.
id_model = read_unigram_lm(args.idmodel)
args.idmodel.close()
vocabulary = id_model.keys()

# Initialize counts from a random sample of non-domain-specific text. Add one to
# all the counts.
selected_counts = word_counts(args.ndssample.read(), vocabulary)
args.ndssample.close()

# Collect the same amount of data there is in the random sample.
selected_text = select_text(args.pages, selected_counts, id_model, args.alpha, sum(selected_counts.values()))

# Recompute the counts from the selected text.
sys.stderr.write('Recomputing counts from selected data.\n')
selected_counts = word_counts(selected_text, vocabulary)

# Filter the rest of the data.
select_text(args.pages, selected_counts, id_model, args.alpha)
