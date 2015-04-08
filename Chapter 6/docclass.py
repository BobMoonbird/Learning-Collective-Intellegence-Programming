import re, math
from pysqlite2 import dbapi2 as sqlite

def getWords(doc):
	splitter = re.compile('\\W+')
	words = [s.lower() for s in splitter.split(doc) if len(s) > 2 and len(s) < 20]
	return dict([(w, 1) for w in words])

def sampleTrain(classifer):
	classifer.train('Nobody owns the water.','good')
  	classifer.train('the quick rabbit jumps fences','good')
  	classifer.train('buy pharmaceuticals now','bad')
  	classifer.train('make quick money at the online casino','bad')
  	classifer.train('the quick brown fox jumps','good')

# --- Classfier Superclass ---

class classifier:

	def __init__(self, getFeatures, filename=None):
		self.fc = {}
		self.cc = {}
		self.getFeatures = getFeatures

	def setDatabase(self, dbname):
		self.con = sqlite.connect(dbname)
		self.con.execute('create table if not exists fc(feature,category,count)')
		self.con.execute('create table if not exists cc(category,count)')

	def train(self, item, cat):
		features = self.getFeatures(item)
		for f in features:
			self.incrementFC(f, cat)
		self.incrementCC(cat)
		self.con.commit()

	def featureProbability(self, f, cat):
		if self.categoryCount(cat) == 0: return 0.0
		return 1.0 * self.featureCount(f, cat) / self.categoryCount(cat)

	def weightedProbability(self, f, cat, prob, weight=1.0, ap=0.5):
		basicProb = prob(f, cat)
		totals = sum([self.featureCount(f, c) for c in self.categories()])
		res = 1.0 * (weight * ap + totals * basicProb) / (weight + totals)
		return res


	# --- Helper Functions ---

	def incrementFC(self, f, cat):
		count = self.featureCount(f, cat)
		if count == 0:
			self.con.execute('insert into fc values ("%s","%s",1)' % (f, cat))
		else:
			self.con.execute('update fc set count=%d where feature="%s" and category="%s"' % (count+1, f, cat))

	def incrementCC(self, cat):
		count = self.categoryCount(cat)
		if count == 0:
			self.con.execute('insert into cc values ("%s",1)' % cat)
		else:
			self.con.execute('update cc set count=%d where category="%s"' % (count+1, cat))

	def featureCount(self, f, cat):
		res = self.con.execute('select count from fc where feature="%s" and category="%s"' %(f, cat)).fetchone()
		if res == None: return 0
		return int(res[0])

	def categoryCount(self, cat):
		res = self.con.execute('select count from cc where category="%s"' % cat).fetchone()
		if res == None: return 0
		return int(res[0])

	def totalCount(self):
		res = self.con.execute('select sum(count) from cc').fetchone()
		if res == None: return 0
		return res[0]

	def categories(self):
		cur = self.con.execute('select category from cc')
		return [d[0] for d in cur]

# --- Naive Bayers Classifer ---

class naivebayers(classifier):

	def __init__(self, getFeatures):
		classifier.__init__(self, getFeatures)
		self.thresholds = {}

	def setThreshold(self, cat, t):
		self.thresholds[cat] = t

	def getThreshold(self, cat):
		if cat not in self.thresholds:
			return 1.0
		else:
			return self.thresholds[cat]

	def docprob(self, item, cat):
		features = self.getFeatures(item)
		p = 1
		for f in features:
			p *= self.weightedProbability(f, cat, self.featureProbability)
		return p

	def prob(self, item, cat):
		catProb = 1.0 * self.categoryCount(cat) / self.totalCount()
		docProb= self.docprob(item, cat)
		return docProb * catProb

	def classify(self, item, default=None):
		probs = {}
		maxProb = 0.0
		best = default
		for cat in self.categories():
			probs[cat] = self.prob(item, cat)
			if probs[cat] > maxProb:
				maxProb = probs[cat]
				best = cat
		for cat in self.categories():
			if best != None and cat != best and probs[cat] * self.getThreshold(best) > probs[best]:
				return default
		return best

# --- Fisher Classifer ---

class fisher(classifier):

	def __init__(self, getFeatures):
		classifier.__init__(self, getFeatures)
		self.minimums = {}

	def setMinimum(self, cat, m):
		self.minimums[cat] = m

	def getMinimum(self, cat):
		if cat not in self.minimums: 
			return 0
		else:
			return self.minimums[cat]

	def cprob(self, f, cat):
		clf = self.featureProbability(f, cat)
		if clf == 0: return 0
		freqSum = sum([self.featureProbability(f, c) for c in self.categories()])
		return 1.0 * clf / freqSum

	def fisherProb(self, item, cat):
		features = self.getFeatures(item)
		p = 1
		for f in features:
			p *= self.weightedProbability(f, cat, self.cprob)
		fscore = -2 * math.log(p)
		return self.invchi2(fscore, len(features) * 2)

	def invchi2(self, chi, df):
		m = chi / 2.0
		s = math.exp(-m)
		term = math.exp(-m)
		for i in range(1, df/2):
			term *= m / i
			s += term
		return min(s, 1.0)

	def classify(self, item, default=None):
		maxProb = 0.0
		best = default
		for cat in self.categories():
			p = self.fisherProb(item, cat)
			if p > self.getMinimum(cat) and p > maxProb:
				maxProb = p
				best = cat
		return best

	


if __name__ == '__main__':
	cl = fisher(getWords)
	cl.setDatabase('test1.db')
	sampleTrain(cl)
	cl2 = naivebayers(getWords)
	cl2.setDatabase('test1.db')
	print cl2.classify('quick money')




