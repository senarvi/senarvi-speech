#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Rules for validating whether a conversational Finnish word
# can be a reduced form of a standard Finnish word.

def is_uoa(ch):
	return ch in ("u", "o", "a")

def is_ie(ch):
	return ch in ("i", "e")

def is_yoa(ch):
	return ch in ("y", "ö", "ä")

def is_vowel(ch):
	return ch in ("o", "o", "a", "i", "e", "y", "ö", "ä")

def is_consonant(ch):
	return not is_vowel(ch)

class ChangeContext:
	def __init__(self, left, center, right, more_left, more_right):
		self.left = left
		self.center = center
		self.right = right
		self.more_left = more_left
		self.more_right = more_right

		# Cache some features.
		self.__left_endswith_vowel = None
		self.__left_endswith_double_vowel = None
		self.__right_startswith_vowel = None

	def match_left(self, x):
		if type(x) is tuple:
			return self.left.sequence in x
		else:
			return self.left.sequence == x

	def left_endswith(self, x):
		return self.left.sequence.endswith(x)

	def left_endswith_vowel(self):
		if self.__left_endswith_vowel is None:
			self.__left_endswith_vowel = is_vowel(self.left.sequence[-1])
		return self.__left_endswith_vowel

	def left_endswith_vowel_and(self, x):
		seq = self.left.sequence
		if type(x) is tuple:
			return \
				any((len(seq) >= len(pattern) + 1) and \
				is_vowel(seq[-len(pattern) - 1]) and \
				(seq.endswith(pattern)) for pattern in x)
		else:
			return \
				(len(self.left.sequence) > len(x)) and \
				is_vowel(self.left.sequence[-len(x) - 1]) and \
				(self.left.sequence[-len(x):] == x)

	# Left context ends in one of the back vowels (u, o, a) and
	# given argument, meaning that suffixes will have a instead
	# of ä and o instead of ö.
	def left_endswith_uoa_and(self, x):
		seq = self.left.sequence
		if type(x) is tuple:
			return \
				any((len(seq) >= len(pattern) + 1) and \
				is_uoa(seq[-len(pattern) - 1]) and \
				(seq.endswith(pattern)) for pattern in x)
		else:
			return \
				(len(self.left.sequence) > len(x)) and \
				is_uoa(self.left.sequence[-len(x) - 1]) and \
				(self.left.sequence[-len(x):] == x)

	# Left context ends in one of the front vowels (i, e) and
	# given argument, meaning that suffixes can have any vowels
	# (depending what vowels exist in the beginning of the word).
	def left_endswith_ie_and(self, x):
		seq = self.left.sequence
		if type(x) is tuple:
			return \
				any((len(seq) >= len(pattern) + 1) and \
				is_ie(seq[-len(pattern) - 1]) and \
				(seq.endswith(pattern)) for pattern in x)
		else:
			return \
				(len(self.left.sequence) > len(x)) and \
				is_ie(self.left.sequence[-len(x) - 1]) and \
				(self.left.sequence[-len(x):] == x)

	# Left context ends in one of the back vowels (y, ö, ä) and
	# given argument, meaning that suffixes will have a instead
	# of ä and o instead of ö.
	def left_endswith_yoa_and(self, x):
		seq = self.left.sequence
		if type(x) is tuple:
			return \
				any((len(seq) >= len(pattern) + 1) and \
				is_yoa(seq[-len(pattern) - 1]) and \
				(seq.endswith(pattern)) for pattern in x)
		else:
			return \
				(len(self.left.sequence) > len(x)) and \
				is_yoa(self.left.sequence[-len(x) - 1]) and \
				(self.left.sequence[-len(x):] == x)

	def left_endswith_double_vowel(self):
		if self.__left_endswith_double_vowel is None:
			self.__left_endswith_double_vowel = \
				(len(self.left.sequence) >= 2) and \
				is_vowel(self.left.sequence[-2]) and \
				is_vowel(self.left.sequence[-1])
		return self.__left_endswith_double_vowel

	def match_right(self, x):
		if type(x) is tuple:
			return self.right.sequence in x
		else:
			return self.right.sequence == x

	def right_startswith(self, x):
		return self.right.sequence.startswith(x)

	def right_startswith_vowel(self):
		if self.__right_startswith_vowel is None:
			self.__right_startswith_vowel = is_vowel(self.right.sequence[0])
		return self.__right_startswith_vowel

	def match_delete(self, x):
		if self.center.is_insert():
			return False
		if type(x) is tuple:
			return self.center.delete in x
		else:
			return self.center.delete == x

	def match_subst(self, x, y):
		if type(x) is tuple:
			if type(y) is tuple:
				return (self.center.delete in x) and (self.center.insert in y)
			else:
				return (self.center.delete in x) and (self.center.insert == y)
		else:
			if type(y) is tuple:
				return (self.center.delete == x) and (self.center.insert in y)
			else:
				return (self.center.delete == x) and (self.center.insert == y)


def validate_change(c):
	# -lla => -l

	# minul(la)ko
	# kairal(la)
	if c.left_endswith_uoa_and("l") and c.match_delete("la"):
		return True
	# kaupungil(la)han
	# puolil(la)kaan
	# siel(lä)kö
	# puolel(la)
	if c.left_endswith_ie_and("l") and c.match_delete(("la", "lä")):
		return True
	# mytyl(lä)
	if c.left_endswith_yoa_and("l") and c.match_delete("lä"):
		return True

	# vielä => viel

	# viel(ä)ki
	if c.left_endswith("viel") and c.match_delete("ä"):
		return True

	# -ssa => -s

	# satamas(sa)
	# talos(sa)
	if c.left_endswith_uoa_and("s") and c.match_delete("sa"):
		return True
	# helsingis(sä)kään
	# talis(sa)
	# ääres(sä)hän
	if c.left_endswith_ie_and("s") and c.match_delete(("sa", "sä")):
		return True
	# vähäs(sä)
	# töllös(sä)
	if c.left_endswith_yoa_and("s") and c.match_delete(("sa", "sä")):
		return True

	# -sta => -st / -lta => -lt

	# kannust(a)
	# radiost(a)kin
	# rannalt(a)
	if c.left_endswith_uoa_and(("st", "lt")) and c.match_delete("a"):
		return True
	# amiksilt(a)
	# pesist(ä)
	# amiksest(a)
	# hesest(ä)
	if c.left_endswith_ie_and(("st", "lt")) and c.match_delete(("a", "ä")):
		return True
	# mytylt(ä)
	# pyynnöst(ä)kään
	# vähäst(ä)
	if c.left_endswith_yoa_and(("st", "lt")) and c.match_delete("ä"):
		return True

	# -ksi => -ks

	# kaks(i)ko
	# miks(i)
	if c.left_endswith("ks") and c.match_delete("i"):
		return True

	# -uun => -uu / -oon => -oo / ...

	# ostetaa(n)han
	# meree(n)
	# ostettii(n)kohan
	# mentii(n)kös
	# varastoo(n)
	# turkuu(n)
	# hullyy(n)
	# mennää(n)
	# töllöö(n)
	if c.left_endswith_double_vowel() and c.match_delete("n"):
		return True

	# -ua => -uu / -oa => -oo / ...

	# suru -a+u
	if c.left_endswith("u") and c.match_subst("a", "u"):
		return True
	# lumo -a+o va
	# aino -a+o staan
	if c.left_endswith("o") and c.match_subst("a", "o"):
		return True
	# biisi -ä+i
	# spagetti -a+i
	if c.left_endswith("i") and c.match_subst(("a", "ä"), "i"):
		return True
	# korke -a+e koulu
	# skebbe -ä+e
	if c.left_endswith("e") and c.match_subst(("a", "ä"), "e"):
		return True
	# pyry -ä+y
	if c.left_endswith("y") and c.match_subst("ä", "y"):
		return True
	# henkilö -ä+ö
	if c.left_endswith("ö") and c.match_subst("ä", "ö"):
		return True

	# -si => -s / -oi => -o / -ui => -u

	# työpaikallas(i)
	# taakses(i)
	# kaipais(i)kaan
	# pienemmäks(i)
	# puhals(i)
	# työns(i)
	# vuos(i)
	# laps(i)
	# ymmärs(i)hän
	# kaus(i)
	# kehu(i)
	# saatto(i)han
	# juuttu(i)
	# roikku(i)
	# arvo(i)tus
	if c.left_endswith(("s", "o", "u")) and c.match_delete("i"):
		return True

	# -kin => -ki / -hin => -hi / -nen => -ne / -sen => -se / -han => -ha / -hän => -hä

	# oletki(n)
	# mukavaaki(n)
	# maihi(n)
	# älyttömi(n)
	# viisasha(n)
	# miksiköhä(n)
	# millaine(n)
	# jonkunlaise(n)
	# oireide(n)
	if c.left_endswith(("ki", "hi", "mi", "ha", "hä", "ne", "se", "de")) and c.match_delete("n") and (c.right is None):
		return True

	if c.left_endswith(("mi", "de")) and c.match_delete("n"):
		return True

	# -ja => -i / -ia => -ii / -jä => -i

	# suru -ja+i
	# talo -ja+i kin
	if c.left_endswith(("u", "o")) and c.match_subst("ja", "i"):
		return True
	# varsi -a+i
	# märki -ä+i
	if c.left_endswith("i") and c.match_subst(("a", "ä"), "i"):
		return True
	# artiste -ja+i han
	# biise -jä+i
	if c.left_endswith("e") and c.match_subst(("ja", "jä"), "i"):
		return True
	# pyry -jä+i
	# mörkö -jä+i
	if c.left_endswith(("y", "ö")) and c.match_subst("jä", "i"):
		return True

	# -ta => -t / -tä => -t

	# kerjuut(a)
	# ainoot(a)
	if c.left_endswith_uoa_and("t") and c.match_delete("a"):
		return True
	# vaikeet(a)
	# mait(a)
	# syit(ä)kin
	# meit(ä)
	# siit(ä)kään
	if c.left_endswith_ie_and("t") and c.match_delete(("a", "ä")):
		return True
	# syyt(ä)
	# miljööt(ä)
	if c.left_endswith_yoa_and("t") and c.match_delete("ä"):
		return True

	# -yt => -t / -ut => -t

	# estelly(t)kään
	# pursunu(t)
	if c.left_endswith(("u", "y")) and c.match_delete("t"):
		return True

	if c.right is not None:
		# -oit- => -ot- / -ais- => -as- / -äin- => -än- / ...

		# pinno(i)te
		# kanso(i)ttaa
		# alo(i)tus
		if c.left_endswith("o") and c.match_delete("i") and c.right.startswith("t"):
			return True
		# ranka(i)su
		# alakohta(i)sta
		# auka(i)see
		# tälla(i)sesta
		# mitta(i)nen
		# puna(i)sen
		# viime(i)nen
		# tuommo(i)nen
		# pito(i)suus
		# sillo(i)n
		# kiukku(i)set
		# repä(i)sit
		# myötä(i)nen
		if c.left_endswith(("a", "o", "e", "u", "ä")) and c.match_delete("i") and c.right_startswith(("n", "s")):
			return True

		# -min- => -m- / -sin- => -s-

		# m(in)ä
		# s(in)äkin
		# m(in)ulla
		if c.match_left(("m", "s")) and c.match_delete("in") and c.right_startswith(("ä", "u")):
			return True

		# -hd- => -h-

		# jah(d)attiin
		# kah(d)eksan
		# eh(d)itty
		# tah(d)ottiin
		# kah(d)en
		# paah(d)ettiin
		if c.left_endswith("h") and c.match_delete("d"):
			return True

		# -adi- => -ai- / ija => ia / ...

		# vaa(d)itaan
		# ve(d)etään
		# huu(d)etaan
		# pu(d)ottiin
		# a(j)attele
		# äi(j)ä
		# palveli(j)oita
		if c.left_endswith_vowel() and c.match_delete(("d", "j")) and c.right_startswith_vowel():
			return True

		# -uo- => -ua-

		# tu -o+a li
		# hu -o+a ne
		if c.left_endswith("u") and c.match_subst("o", "a"):
			return True
		# hi -e+a no
		# ki -e+a hua
		if c.left_endswith("u") and c.match_subst("o", "a"):
			return True

		# sandhi

		# sitte -n+k ki
		# kaike -n+l lisäks
		# ääne -n+m murros
		# asui -n+m paikka
		# kirko -n+r rottaa
		# laste -n+j juhlat
		# joulu -n+v vietto
		if c.match_subst("n", "j") and c.right_startswith("j"):
			return True
		if c.match_subst("n", "k") and c.right_startswith("k"):
			return True
		if c.match_subst("n", "l") and c.right_startswith("l"):
			return True
		if c.match_subst("n", "m") and c.right_startswith("m"):
			return True
		if c.match_subst("n", "m") and c.right_startswith("p"):
			return True
		if c.match_subst("n", "r") and c.right_startswith("r"):
			return True
		if c.match_subst("n", "v") and c.right_startswith("v"):
			return True

		# olet => oot

		# o -le+o t
		# o -le+o tkos
		# o -le+o tpas
		# o -le+o than
		if (not c.more_left) and c.match_left("o") and c.match_subst("le", "o") and c.right_startswith("t"):
			return True
		# o -let+o k -o s
		if (not c.more_left) and c.match_left("o") and c.match_subst("let", "o") and c.match_right("k"):
			return True
		if c.match_left("k") and c.match_delete("o") and c.match_right("s") and (not c.more_right):
			return True

		# nytten => nyt / sitten => sit

		# nyt(ten)ki
		# sit(ten)kö
		if (not c.more_left) and c.match_left(("nyt", "sit")) and c.match_delete("ten"):
			return True

		# -kos => -ks / -kös => -ks

		# palaak(o)s
		# sellaistak(o)s
		if c.left_endswith_uoa_and("k") and c.match_delete("o") and c.match_right("s") and (not c.more_right):
			return True
		# meneek(ö)s
		# tuleek(o)s
		if c.left_endswith_ie_and("k") and c.match_delete(("o", "ö")) and c.match_right("s") and (not c.more_right):
			return True
		# häslääk(ö)s
		if c.left_endswith_yoa_and("k") and c.match_delete("ö") and c.match_right("s") and (not c.more_right):
			return True
		# asu(t)k(o)s
		# makaa(t)k(o)s
		# ostettii(n)k(o)s
		# hallitse(t)k(o)s
		# mene(t)k(ö)s
		# mennää(n)k(ö)s
		if c.more_left and c.match_left("k") and c.match_delete(("o", "ö")) and c.match_right("s") and (not c.more_right):
			return True
	return False

def validate(partitions):
	if len(partitions) < 2:
		return False

	if partitions[0].is_change():
		return False

	for i in range(1, len(partitions) - 1):
		left = partitions[i - 1]
		center = partitions[i]
		right = partitions[i + 1]
		if center.is_change() and not validate_change(ChangeContext(left, center, right, i > 1, i < len(partitions) - 2)):
			return False

	left = partitions[-2]
	center = partitions[-1]
	if center.is_change() and not validate_change(ChangeContext(left, center, None, len(partitions) > 2, False)):
		return False

	return True

