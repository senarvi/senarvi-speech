#!/usr/bin/env python3

import re
import sys

class PronunciationDictionary:
	class Pronunciation:
		def __init__(self, prob, phones):
			self.prob = prob
			self.phones = phones
	
		def __repr__(self):
			return ' '.join(self.phones)
		
		def __len__(self):
			return len(self.phones)
		
		def __iter__(self):
			for phone in self.phones:
				yield phone
		
		def __getitem__(self, index):
			return self.phones[index]
		
	class Word:
		def __init__(self, name):
			self.name = name
			self.pronunciations = []
		
		def __repr__(self):
			return self.name
		
		def __contains__(self, index):
			return index < len(self.pronunciations) and self.pronunciations[index] is not None
		
		def __iter__(self):
			for pronunciation in self.pronunciations:
				if pronunciation is not None:
					yield pronunciation
		
		def __getitem__(self, index):
			return self.pronunciations[index]

		# Returns a dictionary entry as a byte string, word (name)
		# encoded in UTF-8 and pronunciation encoded in ISO-8859-1.
		def dictionary_entry(self):
			result = bytes()
			for pronunciation in self:
				word = self.name + "(" + str(pronunciation.prob) + ") "
				result += word.encode('utf-8')
				result += str(pronunciation).encode('iso-8859-1')
				result += "\n".encode('utf-8')
			return result
			
		def add_pronunciation(self, prob, phones):
			self.pronunciations.append(PronunciationDictionary.Pronunciation(prob, phones))
			
		def set_pronunciation(self, index, prob, phones):
			if index >= len(self.pronunciations):
				self.pronunciations.extend([None] * (index + 1 - len(self.pronunciations)))
			self.pronunciations[index] = PronunciationDictionary.Pronunciation(prob, phones)
		
		def delete_pronunciation(self, index):
			if not index in self:
				raise IndexError("No pronunciation " + str(index) + " for word " + self.name + ".")
			self.pronunciations[index] = None
		
		def num_pronunciations(self):
			result = 0
			for _ in self:
				result = result + 1
			return result

		def is_multiword(self):
			return self.name[0] != '_' and '_' in self.name
		
		# Normalizes probabilities, i.e. the largest probability will be set to
		# one.
		def normalize(self):
			max_prob = float(0)
			for pronunciation in self:
				max_prob = max(pronunciation.prob, max_prob)
			if max_prob > 0:
				for pronunciation in self:
					pronunciation.prob = float(pronunciation.prob) / max_prob
	
	def __init__(self):
		self.words = dict()
		
	def __contains__(self, name):
		return name in self.words
	
	def __iter__(self):
		for word in self.words.values():
			yield word
	
	# Name may contain a colon and a pronunciation ID.
	def __getitem__(self, name):
		colon_pos = name.rfind(':')
		if colon_pos > 0:
			pronunciation_id = int(name[colon_pos+1:])
			name = name[:colon_pos]
			return self.words[name][pronunciation_id]
		else:
			return self.words[name]

	# Reads a dictionary from a file opened in binary mode.	
	def read(self, input_file):
		word_re = re.compile(r'^(\S+)\(([\d\.e\-]+)\)$')
		
		for line in input_file:
			# Decode phones as ISO-8859-1 and the rest of the line as UTF-8.
			space_pos = line.find(int(0x20))
			if space_pos > 0:
				phones = line[space_pos:].decode('iso-8859-1').rstrip().split()
			else:
				phones = []
				space_pos = len(line)

			word = line[:space_pos].decode('utf-8')
			match = word_re.search(word)
			if match is None:
				sys.stderr.write("Could not parse dictionary at word '" + word + "'.\n")
				sys.exit(1)
			name = match.group(1)
			prob = float(match.group(2))

			colon_pos = name.rfind(':')
			if colon_pos > 0:
				# Trailing colon and a number may be used to indicate a
				# pronunciation variant. This is useful when pronunciations need
				# to be separated into different dictionary words.
				pronunciation_id = int(name[colon_pos+1:])
				name = name[:colon_pos]
				if not name in self.words:
					self.words[name] = PronunciationDictionary.Word(name)
				self.words[name].set_pronunciation(pronunciation_id, prob, phones)
			else:
				self.add_word(name, prob, phones)

	def write(self, output_file=sys.stdout.buffer):
		for name in sorted(self.words.keys()):
			output_file.write(self.words[name].dictionary_entry())
	
	def add_word(self, name, prob, phones):
		if not name in self.words:
			self.words[name] = self.Word(name)
		self.words[name].add_pronunciation(prob, phones)
	
	def delete_word(self, name):
		if not name in self.words:
			raise IndexError("No such word in dictionary: " + name)
		del self.words[name]
	
	def delete_pronunciation(self, name, pronunciation_id):
		if not name in self.words:
			raise IndexError("No such word in dictionary: " + name)
		word = self.words[name]
		word.delete_pronunciation(pronunciation_id)
		if word.num_pronunciations() == 0:
			del self.words[name]
	
	# Prune pronunciations with smaller probability than min_prob.
	def prune(self, min_prob):
		for name, word in self.words.items():
			for pronunciation_id, pronunciation in enumerate(word.pronunciations):
				if pronunciation.prob < min_prob:
					word.delete_pronunciation(pronunciation_id)
					if word.num_pronunciations() == 0:
						del self.words[name]
	
	def pronunciations_to_words(self):
		new_words = dict()
		for name, word in self.words.items():
			if len(word.pronunciations) > 1:
				count = 1
				for pronunciation in word.pronunciations:
					if pronunciation is not None:
						new_name = name + ":" + str(count)
						new_words[new_name] = self.Word(new_name)
						new_words[new_name].add_pronunciation(pronunciation.prob, pronunciation.phones)
						count = count + 1
			else:
				new_words[name] = word
		self.words = new_words
