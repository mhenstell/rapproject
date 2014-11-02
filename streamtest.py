import tweepy
import json
import string

# Authentication details. To  obtain these visit dev.twitter.com
consumer_key = '0EjV2v1Cw9qBlQHg1UYW7MQw5'
consumer_secret = 'bhutAMS5DoQMD4pLP4yG57X3kWKJlQ9MdMdq1gSFBf4vepYzGM'
access_token = '2857171541-AsGmwmAgOlogFRsFfgK4oz27UOKZq316SybyxlM'
access_token_secret = 'A9M3Zpmb2zNNbR0W0cCjWE7ivs20pRq8HNh72qg6w322M'

DICTIONARY = "/usr/share/dict/words";
dict = []
trie = None
NodeCount = 0

tweetDict = {}

# The Trie data structure keeps a set of words, organized with one node for
# each letter. Each node has a branch for each letter that may follow it in the
# set of words.
class TrieNode:
    def __init__(self):
        self.word = None
        self.children = {}
	self.WordCount = 0
        global NodeCount
        NodeCount += 1

    def insert( self, word ):
        node = self
        for letter in word:
            if letter not in node.children:
                node.children[letter] = TrieNode()

            node = node.children[letter]

        node.word = word

# The search function returns a list of all words that are less than the given
# maximum distance from the target word
def search( word, maxCost ):
    
    print "searching trie for %s, total trie %s" % (word, trie.WordCount)
    # build first row
    currentRow = range( len(word) + 1 )

    results = []

    # recursively search each branch of the trie
    for letter in trie.children:
        searchRecursive( trie.children[letter], letter, word, currentRow,
            results, maxCost )

    return results

def searchRecursive( node, letter, word, previousRow, results, maxCost ):

    columns = len( word ) + 1
    currentRow = [ previousRow[0] + 1 ]

    # Build one row for the letter, with a column for each letter in the target
    # word, plus one for the empty string at column 0
    for column in xrange( 1, columns ):

        insertCost = currentRow[column - 1] + 1
        deleteCost = previousRow[column] + 1

        if word[column - 1] != letter:
            replaceCost = previousRow[ column - 1 ] + 1
        else:
            replaceCost = previousRow[ column - 1 ]

        currentRow.append( min( insertCost, deleteCost, replaceCost ) )

    # if the last entry in the row indicates the optimal cost is less than the
    # maximum cost, and there is a word in this trie node, then add it.
    if currentRow[-1] <= maxCost and node.word != None:
        results.append( (node.word, currentRow[-1] ) )

    # if any entries in the row are less than the maximum cost, then 
    # recursively search each branch of the trie
    if min( currentRow ) <= maxCost:
        for letter in node.children:
            searchRecursive( node.children[letter], letter, word, currentRow,
                results, maxCost )


# This is the listener, resposible for receiving data
class StdOutListener(tweepy.StreamListener):
    def on_data(self, data):
        # Twitter returns data in JSON format - we need to decode it first
        decoded = json.loads(data)
        # Also, we convert UTF-8 to ASCII ignoring all bad characters sent by users
#        print decoded
	if "user" in decoded and decoded['lang'] == 'en' and "http" not in decoded['text']:
		
		lastWord = decoded['text'].encode('ascii', 'ignore').strip().split(' ')[-1]
		lastWord = lastWord.translate(string.maketrans("", ""), string.punctuation).lower()
		if lastWord in dict:
			if lastWord not in tweetDict:
				tweetDict[lastWord] = [decoded['text'].encode('ascii', 'ignore')]
			
				trie.WordCount += 1
				trie.insert( word )
			else:
				tweetDict[lastWord].append(decoded['text'].encode('ascii', 'ignore'))
			
			results = search(lastWord, 2)
			print results
	
			#print '@%s: %s last: %s' % (decoded['user']['screen_name'], decoded['text'].encode('ascii', 'ignore'), lastWord)
			print "WordCount: %s, td: %s" % (trie.WordCount, len(tweetDict))
			#print ''
        return True

    def on_error(self, status):
        print status

if __name__ == '__main__':
    l = StdOutListener()
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    dict = [word.lower() for word in open(DICTIONARY, "rt").read().split()]
    trie = TrieNode()

    # There are different kinds of streams: public stream, user stream, multi-user streams
    # In this example follow #programming tag
    # For more details refer to https://dev.twitter.com/docs/streaming-apis
    stream = tweepy.Stream(auth, l)
    stream.sample()
