#!/usr/bin/env python3
#
# Reads a dictionary and combines pronunciation variants that have been made
# unique words using pronunciations-to-words.by back into a single word.

import argparse
import sys
from pronunciationdictionary import PronunciationDictionary
from filetypes import BinaryFileType

parser = argparse.ArgumentParser()
parser.add_argument('dictionary', type=BinaryFileType('r'), help='the source dictionary')
args = parser.parse_args()

dictionary = PronunciationDictionary()
dictionary.read(args.dictionary)
dictionary.write()
