import math, os, sys
from pysqlite2 import dbapi2 as sqlite

def dtanh(y):
	return 1.0 - y*y


class searchnet:

	def __init__(self, dbname):
		self.con = sqlite.connect(dbname)

	def __del__(self):
		self.con.close()

	def makeTables(self):
		self.con.execute('create table hiddennode(create_key)')
		self.con.execute('create table wordhidden(fromid, toid, strength)')
		self.con.execute('create table hiddenurl(fromid, toid, strength)')
		self.con.commit()

	def getStrength(self, fromid, toid, layer):
		if layer == 0: table = 'wordhidden'
		else: table = 'hiddenurl'
		res = self.con.execute('select strength from %s where fromid=%d and toid=%d' % (table, fromid, toid)).fetchone()
		if res == None:
			if layer == 0: return -0.2
			if layer == 1: return 0
		return res[0]

	def setStrength(self, fromid, toid, layer, strength):
		if layer == 0: table = 'wordhidden'
		else: table = 'hiddenurl'
		res = self.con.execute('select rowid from %s where fromid=%d and toid=%d' % (table, fromid, toid)).fetchone()
		if res == None:
			self.con.execute('insert into %s (fromid, toid, strength) values (%d, %d, %f)' % (table, fromid, toid, strength))
		else:
			self.con.execute('update %s set strength=%f where rowid=%d' % (table, strength, res[0]))

	def generateHiddenNode(self, wordids, urls):
		if len(wordids) > 3:
			return None
		createKey = ''.join([str(w) for w in wordids])
		res = self.con.execute('select rowid from hiddennode where create_key=%s' % createKey).fetchone()
		if res == None:
			cur = self.con.execute('insert into hiddennode (create_key) values ("%s")' % createKey)
			hiddenid = cur.lastrowid
			for wordid in wordids:
				self.setStrength(wordid, hiddenid, 0, 1.0/len(wordids))
			for urlid in urls:
				self.setStrength(hiddenid, urlid, 1, 0.1)
			self.con.commit()

	def getAllHiddenNodes(self, wordids, urlids):
		l = []
		for wordid in wordids:
			cur = self.con.execute('select toid from wordhidden where fromid=%d' % wordid)
			for row in cur:
				l.append(row[0])
		for urlid in urlids:
			cur = self.con.execute('select fromid from hiddenurl where toid=%d' % urlid)
			for row in cur:
				l.append(row[0])
		return list(set(l))

	def setupNetwork(self, wordids, urlids):
		self.wordids = wordids
		self.hiddenids = self.getAllHiddenNodes(wordids, urlids)
		self.urlids = urlids
		self.ai = [1.0] * len(self.wordids)
		self.ah = [1.0] * len(self.hiddenids)
		self.ao = [1.0] * len(self.urlids)
		self.wi = [[self.getStrength(wordid, hiddenid, 0) for hiddenid in self.hiddenids] for wordid in self.wordids]
		self.wo = [[self.getStrength(hiddenid, urlid, 1) for urlid in self.urlids] for hiddenid in self.hiddenids]

	def feedForward(self, func=math.tanh):
		for i in range(len(self.wordids)):
			self.ai[i] = 1.0
		for j in range(len(self.hiddenids)):
			s = 0.0
			for i in range(len(self.wordids)):
				s += self.ai[i] * self.wi[i][j]
			self.ah[j] = func(s)
		for k in range(len(self.urlids)):
			s = 0.0
			for j in range(len(self.hiddenids)):
				s += self.ah[j] * self.wo[j][k]
			self.ao[k] = func(s)
		return list(self.ao)

	def getResult(self, wordids, urlids):
		self.setupNetwork(wordids, urlids)
		return self.feedForward()

	def backPropagate(self, target, N=0.5):
		outputDeltas = [0.0] * len(self.urlids)
		for k in range(len(self.urlids)):
			error = target[k] - self.ao[k]
			outputDeltas[k] = error * dtanh(self.ao[k])
		hiddenDeltas = [0.0] * len(self.hiddenids)
		for j in range(len(self.hiddenids)):
			error = 0.0
			for k in range(len(self.urlids)):
				error += outputDeltas[k] * self.wo[j][k]
			hiddenDeltas[j] = error * dtanh(self.ah[j])
		for j in range(len(self.hiddenids)):
			for k in range(len(self.urlids)):
				change = outputDeltas[k] * self.ah[j]
				self.wo[j][k] += N * change
		for i in range(len(self.wordids)):
			for j in range(len(self.hiddenids)):
				change = hiddenDeltas[j] * self.ai[i]
				self.wi[i][j] += N * change

	def trainQuery(self, wordids, urlids, selectedURL):
		self.generateHiddenNode(wordids, urlids)
		self.setupNetwork(wordids, urlids)
		self.feedForward()
		targets = [0.0] * len(urlids)
		if urlids.index(selectedURL) != -1:
			targets[urlids.index(selectedURL)] = 1.0
			self.backPropagate(targets)
			self.updateDatabase()

	def updateDatabase(self):
		for i in range(len(self.wordids)):
			for j in range(len(self.hiddenids)):
				self.setStrength(self.wordids[i], self.hiddenids[j], 0, self.wi[i][j])
		for j in range(len(self.hiddenids)):
			for k in range(len(self.urlids)):
				self.setStrength(self.hiddenids[j], self.urlids[k], 1, self.wo[j][k])
		self.con.commit()

if __name__ == '__main__':
	wordids = [101, 102, 103]
	urlids = [201, 202, 203]
	dbname = raw_input('Enter the database name: ')
	if dbname.find('.db') == -1:
		dbname += '.db'
	if not os.path.isfile(dbname):
		mynet = searchnet(dbname)
		mynet.makeTables()
		mynet.generateHiddenNode([101, 103], urlids)
	else:
		mynet = searchnet(dbname)
	print mynet.getResult([101, 103], urlids)
	mynet.trainQuery([101, 103], urlids, 201)
	print mynet.getResult([101, 103], urlids)
	for i in range(30):
		mynet.trainQuery([101, 103], urlids, 201)
		mynet.trainQuery([102, 103], urlids, 202)
		mynet.trainQuery([101], urlids, 203)
	print mynet.getResult([101, 103], urlids)
	print mynet.getResult([102, 103], urlids)
	print mynet.getResult([101], urlids)













