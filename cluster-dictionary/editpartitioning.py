#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# A class that finds a partitioning of two strings into substrings that represent
# the fixed or changed parts between the strings.

class EditPartitioning:
	class FixedSubstring:
		def __init__(self, element):
			self.sequence = str(element)

		def append(self, element):
			self.sequence += element

		def extend(self, substring):
			self.sequence += substring.sequence

		def is_change(self):
			return False

		def is_insert(self):
			return False

		def is_delete(self):
			return False

		def __str__(self):
			return self.sequence


	class ChangedSubstring:
		def __init__(self, op_type, element):
			if op_type == "-":
				self.insert = ""
				self.delete = str(element)
			elif op_type == "+":
				self.insert = str(element)
				self.delete = ""

		def append(self, op_type, element):
			if op_type == "-":
				self.delete += element
			elif op_type == "+":
				self.insert += element

		def extend(self, substring):
			self.insert += substring.insert
			self.delete += substring.delete

		def is_change(self):
			return True

		def is_insert(self):
			return len(self.insert) > 0

		def is_delete(self):
			return len(self.delete) > 0

		def __str__(self):
			result = ""
			if len(self.delete) > 0:
				result += "-" + self.delete
			if len(self.insert) > 0:
				result += "+" + self.insert
			return result


	# Creates a 2D matrix of zeros.
	@staticmethod
	def __zero_matrix(width, height):
		return [[0 for column in range(width)] for row in range(height)]

	# Appends an element to the last partition, or creates a new partition.
	def __append(self, op_type, element):
		if len(self.partitions) > 0:
			if op_type == "=":
				if self.partitions[-1].is_change():
					self.partitions.append(EditPartitioning.FixedSubstring(element))
				else:
					self.partitions[-1].append(element)
			else:
				if self.partitions[-1].is_change():
					self.partitions[-1].append(op_type, element)
				else:
					self.partitions.append(EditPartitioning.ChangedSubstring(op_type, element))
		else:
			if op_type == "=":
				self.partitions.append(EditPartitioning.FixedSubstring(element))
			else:
				self.partitions.append(EditPartitioning.ChangedSubstring(op_type, element))

	# Creates the partitioning using dynamic programming. The algorithm starts
	# from the first element of s1 and s2, so in case of several possible
	# solutions, the common subsequence is fixed closer to the beginning of
	# the strings.
	def __init__(self, s1, s2):
		# Compute LCS length table, which contains the length of the longest
		# common subsequence of suffixes of s1 and s2. (Suffix meaning the
		# elements from certain point to the end of the string.)
		lcs = EditPartitioning.__zero_matrix(len(s1) + 1, len(s2) + 1)
		for j in reversed(range(len(s2))):
			for i in reversed(range(len(s1))):
				if s1[i] == s2[j]:
					lcs[j][i] = lcs[j+1][i+1] + 1
				else:
					lcs[j][i] = max(lcs[j][i+1], lcs[j+1][i])

		# Find the path through the LCS table that maximizes common
		# subsequence length.
		self.partitions = []
		i = 0
		j = 0
		while (i < len(s1)) or (j < len(s2)):
			if (i < len(s1)) and (j < len(s2)) and (s1[i] == s2[j]):
				self.__append("=", s1[i])
				i += 1
				j += 1
			elif (j < len(s2)) and ((i == len(s1)) or (lcs[j+1][i] >= lcs[j][i+1])):
				self.__append("+", s2[j])
				j += 1
			else:
				assert (i < len(s1)) and ((j == len(s2)) or (lcs[j][i+1] > lcs[j+1][i]))
				self.__append("-", s1[i])
				i += 1

	# A hack that tries to obtain a smaller set of partitions in case there are
	# consecutive elements. In case there are several possible solutions, the
	# initial algorithm always fixed the common subsequence closer to the
	# beginning of the strings.
	def clean(self):
		for i in range(len(self.partitions) - 1):
			# Find consecutive substrings a and b where n is a deletion or
			# insertion, and a is fixed but the sequence is the same.
			a = self.partitions[i]
			b = self.partitions[i + 1]
			if not ((not a.is_change()) and b.is_change()):
				continue
			if not (((a.sequence == b.delete) and (not b.is_insert())) or \
			        ((a.sequence == b.insert) and (not b.is_delete()))):
				continue
			# If the substring before a is a change or the substring after b
			# is fixed, swap a and b.
			if ((i > 0) and self.partitions[i - 1].is_change) or \
			   ((i < len(self.partitions) - 2) and (not self.partitions[i + 2].is_change())):
				self.partitions[i], self.partitions[i + 1] = self.partitions[i + 1], self.partitions[i]

		# Merge two consecutive changes or two consecutive fixed substrings.
		new_partitions = []
		i = 0
		while i < len(self.partitions) - 1:
			a = self.partitions[i]
			b = self.partitions[i + 1]
			if ((not a.is_change()) and (not b.is_change())) or \
			   (a.is_change() and b.is_change()):
				a.extend(b)
				i += 2
			else:
				i += 1
			new_partitions.append(a)
		if i < len(self.partitions):
			a = self.partitions[i]
			new_partitions.append(a)
		self.partitions = new_partitions

	def __iter__(self):
		if len(self.partitions) < 2:
			return

		for i in range(1, len(self.partitions) - 1):
			left = self.partitions[i - 1]
			center = self.partitions[i]
			right = self.partitions[i + 1]
			if center.is_change():
				yield EditPartitioning.Context(left, center, right, i > 1, i < len(self.partitions) - 2)

		left = self.partitions[-2]
		center = self.partitions[-1]
		if center.is_change():
			yield EditPartitioning.Context(left, center, None, len(self.partitions) > 2, False)

	def __str__(self):
		result = ""
		for partition in self.partitions:
			result += str(partition) + " "
		return result

