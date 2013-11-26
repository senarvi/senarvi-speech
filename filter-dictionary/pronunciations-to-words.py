#!/usr/bin/env python3
#
# Reads a dictionary and makes different pronunciations unique words by
# appending a colon and a running number to the word name.

import argparse
import sys
from pronunciationdictionary import PronunciationDictionary
from filetypes import BinaryFileType

parser = argparse.ArgumentParser()
parser.add_argument('dictionary', type=BinaryFileType('r'), help='the source dictionary')
args = parser.parse_args()

dictionary = PronunciationDictionary()
dictionary.read(args.dictionary)
dictionary.pronunciations_to_words()
dictionary.write()
