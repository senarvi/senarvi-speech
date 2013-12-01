#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
from bisect import bisect_left, bisect_right
from copy import deepcopy

class WordLattice:
	class Node:
		def __init__(self, id_arg, time):
			self.id = id_arg
			self.time = time
			self.reference_count = 0
		
		def refer(self):
			self.reference_count = self.reference_count + 1
		
		def unrefer(self):
			self.reference_count = self.reference_count - 1
			return self.reference_count == 0
	
	class Link:
		def __init__(self, id_arg, start_node, end_node, word, ac_score,
					lm_score):
			self.id = id_arg
			self.start_node = start_node
			self.end_node = end_node
			self.word = word
			self.ac_score = ac_score
			self.lm_score = lm_score
			
		def __repr__(self):
			return "\t".join([str(self.start_node), str(self.end_node), \
							self.word.encode(sys.stdout.encoding), str(self.ac_score), str(self.lm_score)])
	
	class Path:
		# Constructs a path given a list of node IDs.
		def __init__(self, links = []):
			self.__links = links
		
		def __repr__(self):
			result = "\n".join(str(x) for x in self.__links) + "\n"
			result += "\t\t\t" + str(self.total_ac_score())
			result += "\t" + str(self.total_lm_score())
			return result
			
		def empty(self):
			return len(self.__links) == 0
		
		# Returns the node ID of the final node in this path, or -1 if this is
		# an empty path.
		def final_node(self):
			if self.empty():
				return -1
			else:
				return self.__links[-1].end_node
		
		def append(self, link):
			self.__links.append(link)
		
		# Returns a list of expansions of the path, one for each of the given
		# links.
		def create_expansions(self, links):
			return [WordLattice.Path(self.__links + [x]) for x in links]
		
		def total_ac_score(self):
			return sum(x.ac_score for x in self.__links)
		
		def total_lm_score(self):
			return sum(x.lm_score for x in self.__links)

	# A list of links and nodes.	
	class LNList:
		def __init__(self):
			self.links = []
			self.nodes = []
		
		def extend(self, other):
			self.links.extend(other.links)
			self.nodes.extend(other.nodes)
	
	def __init__(self):
		# A regular expression for fields such as E=997788 or W="that is" in an
		# SLF file.
		self.assignment_re = re.compile(r'(\S+)=(?:"((?:[^\\"]+|\\.)*)"|(\S+))')
		
	def __deepcopy__(self, memo={}):
		result = WordLattice()
		memo[id(self)] = result
		result.__nodes = deepcopy(self.__nodes, memo)
		result.__links = deepcopy(self.__links, memo)
		result.__start_nodes_of_links = deepcopy(self.__start_nodes_of_links, memo)
		result.start_node = self.start_node
		result.end_node = self.end_node
		result.lm_scale = self.lm_scale
		return result
		
	def read_slf(self, input_file):
		self.__nodes = []
		self.__links = []
		self.lm_scale = 1
		
		at_header = True
		for line in input_file:
			if line.startswith('#'):
				continue
			fields = dict([(x[0], x[1] or x[2]) for x in self.assignment_re.findall(line.rstrip())])
			if at_header:
				if 'start' in fields:
					self.start_node = int(fields['start'])
				if 'end' in fields:
					self.end_node = int(fields['end'])
				if 'lmscale' in fields:
					self.lm_scale = float(fields['lmscale'])
				if ('I' in fields) or ('J' in fields):
					at_header = False
			if not at_header:
				if 'I' in fields:
					node_id = int(fields['I'])
					if 't' in fields:
						node_time = int(fields['t'])
					else:
						node_time = 0
					self.__nodes.append(self.Node(node_id, node_time))
				elif 'J' in fields:
					link_id = int(fields['J'])
					start_node = int(fields['S'])
					end_node = int(fields['E'])
					word = fields['W']
					if 'a' in fields:
						ac_score = float(fields['a'])
					else:
						ac_score = 0
					lm_score = float(fields['l'])
					self.__links.append(self.Link(link_id, start_node, end_node,
											word, ac_score, lm_score))

		if len(self.__nodes) == 0:
			raise Exception("No nodes read.")
		if not hasattr(self, 'start_node'):
			self.start_node = self.__nodes[0]
		if not hasattr(self, 'end_node'):
			self.end_node = self.__nodes[-1]
		
		self.__nodes_updated()
		self.__links_updated()
		
		self.__nodes[self.start_node].refer()
		for link in self.__links:
			self.__nodes[link.end_node].refer()

	def write_slf(self, output_file):
		output_file.write("# Header\n")
		output_file.write("VERSION=1.1\n")
		output_file.write("base=10\n")
		output_file.write("dir=f\n")
		output_file.write("lmscale=" + str(self.lm_scale) + "\n")
		output_file.write("start=" + str(self.start_node) + "\n")
		output_file.write("end=" + str(self.end_node) + "\n")
		output_file.write("NODES=" + str(len(self.__nodes)))
		output_file.write(" LINKS=" + str(len(self.__links)) + "\n")
		
		output_file.write("# Nodes\n")
		for node in self.__nodes:
			output_file.write("I=" + str(node.id))
			output_file.write("\tt=" + str(node.time) + "\n")
		
		output_file.write("# Links\n")
		for link in self.__links:
			output_file.write("J=" + str(link.id))
			output_file.write("\tS=" + str(link.start_node))
			output_file.write("\tE=" + str(link.end_node))
			output_file.write("\tW=" + link.word)
			output_file.write("\ta=" + str(link.ac_score))
			output_file.write("\tv=0")
			output_file.write("\tl=" + str(link.lm_score) + "\n")
	
	# Finds a path from start node to end node through given words.
	def find_paths(self, words):
		tokens = self.expand_path_to_null_links(self.Path())
		for word in words:
			new_tokens = []
			for path in tokens:
				new_tokens.extend(self.find_extensions(path, word))
			tokens = new_tokens
			new_tokens = []
			for path in tokens:
				new_tokens.extend(self.expand_path_to_null_links(path))
			tokens = new_tokens
			print(len(tokens), "tokens @", word)
			if tokens == []:
				return []
		result = []
		for path in tokens:
			if path.final_node() == self.end_node:
				result.append(path)
		return result
	
	# Returns the range of links with given start node.
	def links_from(self, node_id):
		first = bisect_left(self.__start_nodes_of_links, node_id)
		last = bisect_right(self.__start_nodes_of_links, node_id)
		return self.__links[first:last]
	
	# Returns a list of paths that have been formed my advancing from given path
	# to all the !NULL links and recursively to the next !NULL links. the given
	# path is also included. If the given path is empty, starts from the global
	# start node.
	def expand_path_to_null_links(self, path):
		if path.empty():
			start_node = self.start_node
		else:
			start_node = path.final_node()
		
		expansion_links = []
		for link in self.links_from(start_node):
			if link.word == "!NULL":
				expansion_links.append(link)
		expanded_paths = path.create_expansions(expansion_links)
		
		result = [path]
		for expanded_path in expanded_paths:
			result.extend(self.expand_path_to_null_links(expanded_path))
		return result
	
	# Returns a list of paths that have been formed by advancing from given path
	# to all the links with given word.
	def find_extensions(self, path, word):
		links = []
		for link in self.links_from(path.final_node()):
			if link.word == word:
				links.append(link)
		return path.create_expansions(links)
	
	# Returns the set of words present in this lattice.
	def words(self):
		result = set()
		for link in self.__links:
			if link.word != '!NULL':
				result.add(link.word)
		return result
	
	# Returns the set of node IDs present in this lattice.
	def node_ids(self):
		return set(x.id for x in self.__nodes)
	
	# Returns the set of reachable nodes in the lattice.
	def reachable_nodes(self, start_node=None):
		if start_node is None:
			start_node = self.start_node
		
		result = set([start_node])
		for link in self.links_from(start_node):
			result.update(self.reachable_nodes(link.end_node))
		return result
	
	# Returns the set of unreachable nodes in the lattice.
	def unreachable_nodes(self):
		return self.node_ids() - self.reachable_nodes()
	
	# Remove links that contain a word from the given list.
	def remove_words(self, words):
		to_delete = self.LNList()
		for link in self.__links:
			if link.word in words:
				to_delete.links.append(link.id)
				to_delete.extend(self.__unlink(link.end_node))
		
		for link in self.__links:
			if (link.start_node in to_delete.nodes) or \
			   (link.end_node in to_delete.nodes):
				to_delete.links.append(link.id)
		
		if self.end_node in to_delete.nodes:
			self.end_node = -1
		
		self.__links = [x for x in self.__links if not x.id in to_delete.links]
		self.__nodes = [x for x in self.__nodes if not x.id in to_delete.nodes]
		self.__links_updated()
		self.__nodes_updated()
	
	# Returns a copy of the lattice with all the links containing any of the
	# given words removed.
	def without_words(self, words):
		result = deepcopy(self)
		result.remove_words(words)
		return result
	
	# Decrements the reference count of a node. If the reference count drops to
	# zero, marks the node and all the outgoing links for deletion, and
	# repeats the process to all the nodes behind the outgoing links. Returns
	# two lists: the links marked for deletion, and the nodes marked for
	# deletion.
	def __unlink(self, node_id):
		to_delete = self.LNList()
		if (self.__nodes[node_id].unrefer()):
			to_delete.nodes.append(node_id)
			out_links = self.links_from(node_id)
			for link in out_links:
				to_delete.links.append(link.id)
				to_delete.extend(self.__unlink(link.end_node))
		return to_delete
	
	# Keeps links sorted by start node so that we can find all the out links
	# from given node fast. Has to be called after self.__links is changed.
	def __links_updated(self):
		self.__links.sort(key = lambda x: x.start_node)
		# There's no key= parameter for bisect functions so we create a separate
		# list of the start nodes of each link that we use just for searching.
		self.__start_nodes_of_links = [x.start_node for x in self.__links]

	# Give nodes linear IDs so that they can be indexed by node ID.
	def __nodes_updated(self):
		mapping = {}
		for index, node in enumerate(self.__nodes):
			mapping[node.id] = index
			node.id = index
		for link in self.__links:
			link.start_node = mapping[link.start_node]
			link.end_node = mapping[link.end_node]
		if self.start_node != -1:
			self.start_node = mapping[self.start_node]
		if self.end_node != -1:
			self.end_node = mapping[self.end_node]
