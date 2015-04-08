import feedparser, re, functools
import docclass, clusters
import numpy as np
import nmf

def getFeedList(filename):
	feedlist = []
	fp = open(filename, 'r')
	for line in fp:
		feedlist.append(line.strip())
	fp.close()
	return feedlist

def stripHTML(html):
	stripped, isTag = '', 0
	for content in html:
		if content == '<':
			isTag = 1
		elif content == '>':
			isTag = 0
			stripped += ' '
		elif isTag == 0:
			stripped += content
	return stripped

def separateWords(text):
	splitter = re.compile('\\W+')
	return [s.lower() for s in splitter.split(text) if len(s) > 3]

def getArticleWords(feedlist, limit=20):
	allWords = {}
	articleWords = []
	articleTitles = []
	entryIndex = 0
	
	for feed in feedlist:
		if limit == 0: break
		f = feedparser.parse(feed)
		for entry in f.entries:
			if entry.title in articleTitles: continue
			text = str(entry.title.encode('utf-8')) + stripHTML(str(entry.description.encode('utf-8')))
			words = separateWords(text)
			articleWords.append({})
			articleTitles.append(str(entry.title.encode('utf-8')))
			for word in words:
				allWords.setdefault(word, 0)
				articleWords[entryIndex].setdefault(word, 0)
				allWords[word] += 1
				articleWords[entryIndex][word] += 1
			entryIndex += 1
		limit -= 1
	return allWords, articleWords, articleTitles

def makeWordsMatrix(allWords, articleWords):
	wordVector = []
	for word, count in allWords.iteritems():
		if count > 3 and count < len(articleWords) * 0.6:
			wordVector.append(word)
	matrix = [[doc[word] if word in doc else 0 for word in wordVector] for doc in articleWords]
	return matrix, wordVector

def makeWordsMatrixFeatures(row, wordVector):
	return [wordVector[wordidx] for wordidx in range(len(row)) if row[wordidx] > 0]

def showFeatures(w, h, titles, wordVector, output='features.txt', topW=6, topA=3):
	outputFile = open(output, 'w')
	k, n = np.shape(h)
	topPatterns = [[] for i in range(len(titles))]
	patternNames = []

	for i in range(k):
		wordlist = [(h[i, j], wordVector[j]) for j in range(n)]
		wordlist = sorted(wordlist, reverse=True)
		topWordList = [wordlist[j][1] for j in range(topW)]
		outputFile.write(str(topWordList) + '\n')
		patternNames.append(topWordList)
		featureList = []
		for j in range(len(titles)):
			featureList.append((w[j, i], titles[j]))
			topPatterns[j].append((w[j, i], i, titles[j]))
		featureList = sorted(featureList, reverse=True)
		topArticleList = [featureList[j][1] for j in range(topA)]
		outputFile.write(str(topArticleList) + '\n')
	outputFile.close()
	return topPatterns, patternNames

def showArticles(titles, topPatterns, patternNames, output='articles.txt', topA=3):
	outputFile = open(output, 'w')
	for j in range(len(titles)):
		outputFile.write(titles[j] + '\n')
		topPatterns[j] = sorted(topPatterns[j], reverse=True)
		for i in range(topA):
			outputFile.write(str(topPatterns[j][i][0]) + ' ' + str(patternNames[topPatterns[j][i][1]]) + '\n')
		outputFile.write('\n')
	outputFile.close()

if __name__ == '__main__':

	feedlist = getFeedList('feedlist.txt')
	allWords, articleWords, articleTitles = getArticleWords(feedlist)
	wordMatrix, wordVector = makeWordsMatrix(allWords, articleWords)

	# Naive Bayers Classification
	# getFeatures = functools.partial(makeWordsMatrixFeatures, wordVector=wordVector)
	# classifier = docclass.naivebayers(getFeatures)
	# classifier.setDatabase('newsfeed.db')
	# classifier.train(wordMatrix[0], 'thing')
	# classifier.train(wordMatrix[1], 'thing')
	# classifier.train(wordMatrix[2], 'solution')
	# classifier.train(wordMatrix[3], 'solution')
	# classifier.train(wordMatrix[4], 'solution')
	# classifier.train(wordMatrix[5], 'thing')
	# classifier.train(wordMatrix[6], 'solution')
	# classifier.train(wordMatrix[7], 'thing')
	# print classifier.classify(wordMatrix[8])
	# print classifier.classify(wordMatrix[9])

	# Clustering
	# cluster = clusters.hcluster(wordMatrix)
	# clusters.drawDendrogram(cluster, articleTitles, jpeg='newsclusters.jpg')
	# cluster = clusters.hcluster(clusters.rotateMatrix(wordMatrix))
	# clusters.drawDendrogram(cluster, wordVector, jpeg='wordclusters.jpg')

	# NMF
	nmfWordMatrix = np.matrix(wordMatrix)
	weights, feats = nmf.factorize(nmfWordMatrix, k=20, maxIterations=50)
	topPatterns, patternNames = showFeatures(weights, feats, articleTitles, wordVector)
	showArticles(articleTitles, topPatterns, patternNames)



	








