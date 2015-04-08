import urllib2, re, os.path
from BeautifulSoup import *
from urlparse import urljoin
from pysqlite2 import dbapi2 as sqlite
import neuralnetwork

ignoreWords = set(['the', 'of', 'to', 'and', 'a', 'in', 'is', 'it'])

class crawler:
	def __init__(self, dbname):
		self.con = sqlite.connect(dbname)

	def __del__(self):
		self.con.close()

	def dbcommit(self):
		self.con.commit()

	def getEntryID(self, table, field, value, createNew=True):
		cur = self.con.execute('select rowid from %s where %s="%s"' % (table, field, value))
		res = cur.fetchone()
		if res == None:
			cur = self.con.execute('insert into %s(%s) values ("%s")' % (table, field, value))
			return cur.lastrowid
		else:
			return res[0]

	def addToIndex(self, url, soup):
		if self.isIndexed(url):
			return
		print 'Indexing %s' % url
		text = self.getTextOnly(soup)
		words = self.separateWords(text)
		urlid = self.getEntryID('urllist', 'url', url)
		for i in range(len(words)):
			word = words[i]
			if word in ignoreWords:
				continue
			wordid = self.getEntryID('wordlist', 'word', word)
			self.con.execute('insert into wordlocation(urlid, wordid, location) values (%d,%d,%d)' % (urlid, wordid, i))

	def getTextOnly(self, soup):
		string = soup.string
		if string == None:
			c = soup.contents
			restext = ''
			for t in c:
				subtext = self.getTextOnly(t)
				restext += subtext + '\n'
			return restext
		else:
			return string.strip()

	def separateWords(self, text):
		splitter = re.compile('\\W*')
		return [word.lower() for word in splitter.split(text) if word != '']

	def isIndexed(self, url):
		u = self.con.execute('select rowid from urllist where url="%s"' % url).fetchone()
		if u != None:
			v = self.con.execute("select * from wordlocation where urlid=%d" % u[0]).fetchone()
			if v != None:
				return True
		return False

	def addLinkRef(self, urlFrom, urlTo, linkText):
		pass

	def crawl(self, pages, depth=2):
		for i in range(depth):
			newpages = set()
			for page in pages:
				try:
					c = urllib2.urlopen(page)
				except:
					print 'Could not open %s' % page
					continue
				soup = BeautifulSoup(c.read())
				self.addToIndex(page, soup)
				links = soup('a')
				for link in links:
					if ('href' in dict(link.attrs)):
						url = urljoin(page, link['href'])
						if url.find("'") != -1:
							continue
						url = url.split('#')[0]
						if url[0:4] == 'http' and not self.isIndexed(url):
							newpages.add(url)
						LinkText = self.getTextOnly(soup)
						self.addLinkRef(page, url, LinkText)
				self.dbcommit()
			pages = newpages

	def createIndexTables(self):
		self.con.execute('create table urllist(url)')
		self.con.execute('create table wordlist(word)')
		self.con.execute('create table wordlocation(urlid,wordid,location)')
		self.con.execute('create table link(fromid integer,toid integer)')
		self.con.execute('create table linkwords(wordid,linkid)')
		self.con.execute('create index wordidx on wordlist(word)')
		self.con.execute('create index urlidx on urllist(url)')
		self.con.execute('create index wordurlidx on wordlocation(wordid)')
		self.con.execute('create index urltoidx on link(toid)')
		self.con.execute('create index urlfromidx on link(fromid)')
		self.dbcommit()

	def calculatePageRank(self, iterations=20):
		self.con.execute('drop table if exists pagerank')
		self.con.execute('create table pagerank(urlid primary key, score)')
		self.con.execute('insert into pagerank select rowid, 1.0 from urllist')
		self.dbcommit()
		print 'Calculating Page Rank ...'
		for i in range(iterations):
			print 'Complete %d/%d...' % (i + 1, iterations)
			for (urlid,) in self.con.execute('select rowid from urllist'):
				pagerank = 0.15
				for (linker,) in self.con.execute('select distinct fromid from link where toid=%d' % urlid):
					linkingpagerank = self.con.execute('select score from pagerank where urlid=%d' % linker).fetchone()[0]
					linkingcount = self.con.execute('select count(*) from link where fromid=%d' % linker).fetchone()[0]
					pagerank += 0.85*linkingpagerank/linkingcount
				self.con.execute('update pagerank set score=%f where urlid=%d' % (pagerank, urlid))
			self.dbcommit()

class searcher:
	def __init__(self, dbname):
		self.con = sqlite.connect(dbname)

	def __del__(self):
		self.con.close()

	def getMatchRows(self, qStr):
		fieldlist = 'w0.urlid'
		tablelist = ''
		clauselist = ''
		wordids = []
		words = qStr.split()
		tablenumber = 0
		for word in words:
			wordrow = self.con.execute("select rowid from wordlist where word=('%s')" % word).fetchone()
			if wordrow != None:
				wordid = wordrow[0]
				wordids.append(wordid)
				if tablenumber > 0:
					tablelist += ','
					clauselist += ' and '
					clauselist += 'w%d.urlid=w%d.urlid and ' % (tablenumber - 1, tablenumber)
				fieldlist += ',w%d.location' % tablenumber
				tablelist += 'wordlocation w%d' % tablenumber
				clauselist += 'w%d.wordid=%d' % (tablenumber, wordid)
				tablenumber += 1
		if tablelist == '' and clauselist == '':
			return [], []
		fullquery = 'select %s from %s where %s' % (fieldlist, tablelist, clauselist)
		cur = self.con.execute(fullquery)
		rows = [row for row in cur]
		return rows, wordids

	def getScoredList(self, rows, wordids):
		totalscores = dict([(row[0], 0) for row in rows])
		weights = [(1.0, self.frequencyScore(rows)), (1.0, self.locationScore(rows)), (1.0, self.pagerankScore(rows)), \
				  (1.0, self.linktextScore(rows, wordids)), (1.0, self.neuralNetwordScore(rows, wordids)), (0.1, self.distanceScore(rows)), (0.1, self.inboundLinkScore(rows))]
		for (weight, scores) in weights:
			for url in totalscores:
				totalscores[url] += weight * scores[url]
		return totalscores

	def getUrlName(self, identity):
		return self.con.execute('select url from urllist where rowid=%d' % identity).fetchone()[0]

	def query(self, q):
		rows, wordids = self.getMatchRows(q)
		scores = self.getScoredList(rows, wordids)
		rankedscores = sorted([(score, url) for (url, score) in scores.iteritems()], reverse=True)
		for (score, urlid) in rankedscores[:10]:
			print 'Score: %f\tURL: %s' % (score, self.getUrlName(urlid))
		return wordids, [r[1] for r in rankedscores[:10]]

	def normalizeScores(self, scores, smallIsBetter=False):
		if len(scores) == 0:
			return scores
		minimal = 0.00001
		if smallIsBetter:
			minscore = min(scores.values())
			return dict([(u, 1.0*minscore/max(minimal, c)) for (u, c) in scores.iteritems()])
		else:
			maxscore = max([max(scores.values()), minimal])
			return dict([(u, 1.0*c/maxscore) for (u, c) in scores.iteritems()])

	def frequencyScore(self, rows):
		counts = dict([(row[0], 0) for row in rows])
		for row in rows:
			counts[row[0]] += 1
		return self.normalizeScores(counts)

	def locationScore(self, rows):
		maximal = 1000000
		locations = dict([(row[0], maximal) for row in rows])
		for row in rows:
			loc = sum(row[1:])
			if loc < locations[row[0]]:
				locations[row[0]] = loc
		return self.normalizeScores(locations, smallIsBetter=True)

	def distanceScore(self, rows):
		if len(rows[0]) <= 2:
			return dict([(row[0], 1.0) for row in rows])
		maximal = 1000000
		distances = dict([(row[0], maximal) for row in rows])
		for row in rows:
			dist = sum([abs(row[i] - row[i - 1]) for i in range(2, len(row))])
			if dist < distances[row[0]]:
				distances[row[0]] = dist
		return self.normalizeScores(distances, smallIsBetter=True)

	def inboundLinkScore(self, rows):
		uniqueURLs = set([row[0] for row in rows])
		inboundCount = dict([(u, self.con.execute('select count(*) from link where toid=%d' % u).fetchone()[0]) for u in uniqueURLs])
		return self.normalizeScores(inboundCount)

	def pagerankScore(self, rows):
		pageranks = dict([(row[0], self.con.execute('select score from pagerank where urlid=%d' % row[0]).fetchone()[0]) for row in rows])
		maxrank = max(pageranks.values())
		normalizedScores = dict([(u, 1.0*pagerank/maxrank) for (u, pagerank) in pageranks.iteritems()])
		return normalizedScores

	def linktextScore(self, rows, wordids):
		linkscores = dict([(row[0], 0) for row in rows])
		for wordid in wordids:
			cur = self.con.execute('select link.fromid, link.toid from linkwords, link where wordid=%d and linkwords.linkid=link.rowid' % wordid)
			for (fromid, toid) in cur:
				if toid in linkscores:
					pagerank = self.con.execute('select score from pagerank where urlid=%d' % fromid).fetchone()[0]
					linkscores[toid] += pagerank
		maxscore = max(linkscores.values())
		normalizedScores = dict([(u, 1.0*score/maxscore) for (u, score) in linkscores.iteritems()])
		return normalizedScores

	def neuralNetwordScore(self, rows, wordids):
		urlids = [urlid for urlid in set([row[0] for row in rows])]
		nnres = mynet.getResult(wordids, urlids)
		scores = dict([(urlids[i], nnres[i]) for i in range(len(urlids))])
		return self.normalizeScores(scores)


if __name__ == '__main__':
	pagelist = []
	seedpage = raw_input('Enter the website page address: ')
	if seedpage.find('http://') == -1:
		seedpage = 'http://' + seedpage
	pagelist.append(seedpage)
	dbname = raw_input('Enter the database name: ')
	if dbname.find('.db') == -1:
		dbname += '.db'
	crawler = crawler(dbname)
	if not os.path.isfile(dbname):
		crawler.createIndexTables()
		crawler.crawl(pagelist)
	crawler.calculatePageRank()
	searcher = searcher(dbname)
	mynet = neuralnetwork.searchnet('nn.db')
	while True:
		qStr = raw_input('Enter the query string (press Enter to quit): ')
		if qStr == '' or qStr == '\n':
			break
		searcher.query(qStr)