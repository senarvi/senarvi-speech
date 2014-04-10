#!/usr/bin/env python3
#
# Reads a dictionary and a file that contains a list of words that should be
# removed. Then prints the dictionary with those words excluded.

import argparse
import sys
import codecs
from pronunciationdictionary import PronunciationDictionary
from filetypes import TextFileType, BinaryFileType

parser = argparse.ArgumentParser()
parser.add_argument('dictionary', type=BinaryFileType('r'), help='the source dictionary')
parser.add_argument('wordlist', type=TextFileType('r'), help='file containing a list of words to be excluded')
parser.add_argument('-c', '--count', type=int, dest='exclude_count', default=None,
                    help="number of dictionary entries to remove (the default is all the entries in the word list)")
parser.add_argument('-k', '--keep-words', action='store_true', default=False,
                    help="leave at least one pronunciation for every word")
parser.add_argument('--count-kept', action='store_true', default=False,
                    help="when using --keep-words, count is the number of entries considered, even if they were not removed")
args = parser.parse_args()

words = args.wordlist.readlines()
args.wordlist.close()
words = [x.rstrip() for x in words]

dictionary = PronunciationDictionary()
dictionary.read(args.dictionary)
args.dictionary.close()

num_deleted = 0
for word in words:
	if (args.exclude_count is not None) and (num_deleted >= args.exclude_count):
		break
	# A trailing colon and number marks a pronunciation variant.
	colon_pos = word.rfind(':')
	if colon_pos > 0:
		pronunciation_id = int(word[colon_pos+1:])
		word = word[:colon_pos]
		if args.keep_words:
			if dictionary[word].num_pronunciations() <= 1:
				if args.count_kept:
					num_deleted += 1
				continue
		dictionary.delete_pronunciation(word, pronunciation_id)
	else:
		if args.keep_words:
			if args.count_kept:
				num_deleted += 1
			continue
		dictionary.delete_word(word)
	num_deleted += 1

dictionary.write()
