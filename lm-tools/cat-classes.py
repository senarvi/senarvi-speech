#!/usr/bin/env python3
#
# Concatenates class definition files and renames the classes so that class
# definitions from different files will be uniquely named. Also, ignores
# repeated <s>, </s>, and <unk> classes.

import argparse
import sys
from filetypes import TextFileType

class Names:
	def __init__(self, reserved):
		self.reserved = set(reserved)
		self.last_id = 1
	
	def add(self, name):
		if name in self.reserved:
			while True:
				name = "%05d" % self.last_id
				name = "CLASS-" + name
				if not name in self.reserved:
					self.reserved.add(name)
					return name
				self.last_id = self.last_id + 1
		else:
			self.reserved.add(name)
			return name

parser = argparse.ArgumentParser()
parser.add_argument('input', type=TextFileType('r'), nargs='+', help='input class definition file')
args = parser.parse_args()

print("CLASS-00001 1 <unk>")
print("CLASS-00002 1 <s>")
print("CLASS-00003 1 </s>")

# Names that have been taken already.
names = Names(["CLASS-00001", "CLASS-00002", "CLASS-00003"])

for input_file in args.input:
	# A mapping from class name in this input file to class name in output.
	name_map = dict()
	
	for line in input_file:
		words = line.split()
		if len(words) == 0:
			continue
		if len(words) < 2:
			print("Probability or words missing from class definition:", file=sys.stderr)
			print(" ".join(words), file=sys.stderr)
			sys.exit(1)

		name = words[0]
		prob = words[1]
		items = words[2:]

		if len(items) == 1:
			if items[0] == "<unk>" or items[0] == "<s>" or items[0] == "</s>":
				continue

		if not name in name_map:
			name_map[name] = names.add(name)
		name = name_map[name]

		print(name, prob, " ".join(items))
