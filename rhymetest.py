import nltk

def rhyme(inp, level):
	entries = nltk.corpus.cmudict.entries()
	syllables = [(word, syl) for word, syl in entries if word == inp]
	rhymes = []
	for (word, syllable) in syllables:
		rhymes += [word for word, pron in entries if pron[-level:] == syllable[-level:]]
	return set(rhymes)

print rhyme('test', 0)
