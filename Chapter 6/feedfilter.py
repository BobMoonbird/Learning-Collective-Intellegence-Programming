import feedparser, re
import docclass

def read(feed, classifier):
	f = feedparser.parse(feed)
	for entry in f['entries']:
		print ""
		print '-----'
		print 'Title:\t' + entry['title'].encode('utf-8')
		print 'Publisher:\t' + entry['publisher'].encode('utf-8')
		print ""
		print entry['summary'].encode('utf-8')
		print 'Guess:\t' + str(classifier.classify(entry))
		cl = raw_input('Enter category: ')
		if cl == "": return
		classifier.train(entry, cl)

def getEntryFeatures(entry):
	splitter = re.compile('\\W+')
	features = {}
	titlewords = [s.lower() for s in splitter.split(entry['title']) if len(s) > 2 and len(s) < 20]
	for title in titlewords:
		features['Title:' + title] = 1
	summarywords = [s.lower() for s in splitter.split(entry['summary']) if len(s) > 2 and len(s) < 20]
	uppercaseCount = 0
	for i in range(len(summarywords)):
		word = summarywords[i]
		features[word] = 1
		if word.isupper():
			uppercaseCount += 1
		if i < len(summarywords) - 1:
			pair = ' '.join(summarywords[i:i+2])
			features[pair] = 1
	features['Publisher:' + entry['publisher']] = 1
	uppercaseFreq = 1.0 * uppercaseCount / len(summarywords)
	if uppercaseFreq > 0.3:
		features['UPPERCASE'] = 1
	return features


if __name__ == '__main__':
	classifier = docclass.fisher(getEntryFeatures)
	classifier.setDatabase('python_feed.db')
	feed = 'python_search.xml'
	read(feed, classifier)