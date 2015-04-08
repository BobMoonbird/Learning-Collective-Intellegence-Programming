import feedparser
import re
import random
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def getwordcounts(url):
	d = feedparser.parse(url)
	wordcount = {}
	for e in d.entries:
		if 'summary' in e: 
			summary = e['summary']
		else:
			summary = e['description']
		words = getwords(e.title + ' ' + summary)
		for word in words:
			wordcount.setdefault(word, 0)
			wordcount[word] += 1
	if 'title' in d.feed:
		title = d.feed.title
	else:
		title = 'unknown'
	return title, wordcount

def getwords(html):
	txt = re.compile(r'<[^>]+>').sub('', html)
	words = re.compile(r'[^A-Z^a-z]+').split(txt)
	return [word.lower() for word in words if word != '']

if __name__ == '__main__':
	apcount = {}
	wordcounts = {}
	length = 0
	limit = 30
	for feedurl in open('feedlist.txt'):		
		title, wordcount = getwordcounts(feedurl)
		if title == 'unknown':
			continue
		wordcounts[title] = wordcount
		for word, count in wordcount.iteritems():
			apcount.setdefault(word, 0)
			if (count > 1):
				apcount[word] += 1
		length += 1
		if length == limit:
			break
	wordlist = []
	for word, count in apcount.iteritems():
		frac = float(count) / length
		if frac > 0.1 and frac < 0.5:
			wordlist.append(str(word))
	
	output = open('blogdata.txt', 'w')
	output.write('Blog')
	for word in wordlist:
		output.write('\t%s' % word)
	output.write('\n')
	for blog, wordcount in wordcounts.iteritems():
		output.write(unicode(blog))
		for word in wordlist:
			if word in wordcount:
				output.write('\t%d' % wordcount[word])
			else:
				output.write('\t0')
		output.write('\n')

