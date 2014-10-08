## find-reduced-forms.py

Reads a colloquial and a standard Finnish vocabulary, and for each (reduced)
word form that exists only in the colloquial vocabulary (e.g. "sitkö"), finds
its base form (e.g. "sittenkö").

## finnishreductions.py

Rules for validating whether a conversational Finnish word can be a reduced
form of a standard Finnish word. Used by find-reduced-forms.py.

## editpartitioning.py

A class that finds a partitioning of two strings into substrings that
represent the fixed or changed parts between the strings.

## word-diffs.py

Reads a list of word pairs, one pair per line, and shows the edit operations
needed to transform one word into the other.
