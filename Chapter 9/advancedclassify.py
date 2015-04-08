import pylab, urllib2, math, time
from xml.dom.minidom import parseString
from svmutil import *

loc_cache = {}

### Data Processing Functions ###

class matchrow:
	def __init__(self, row, allnum=False):
		if allnum:
			self.data = [float(row[i]) for i in range(len(row) - 1)]
		else:
			self.data = row[0:len(row) - 1]
		self.match = int(row[len(row) - 1])

def loadmatch(filename, allnum=False):
	rows = []
	fp = open(filename, 'r')
	for line in fp:
		rows.append(matchrow(line.split(','), allnum))
	fp.close()
	return rows

def loadNumerical(filename):
	oldrows = loadmatch(filename)
	newrows = []
	for row in oldrows:
		d = row.data
		res = row.match
		data = (float(d[0]), yesOrNo(d[1]), yesOrNo(d[2]), \
				float(d[5]), yesOrNo(d[6]), yesOrNo(d[7]), \
				matchCount(d[3], d[8]), getMilesDistance(d[4], d[9]), res)
		newrows.append(matchrow(data))
	return newrows

def scaledata(rows):
	low = [999999999.0] * len(rows[0].data)
	high = [-999999999.0] * len(rows[0].data)
	for row in rows:
		d = row.data
		for i in range(len(d)):
			if d[i] < low[i]: low[i] = d[i]
			if d[i] > high[i]: high[i] = d[i]
	def scaleFunction(d):
		return [1.0 * (d[i] - low[i])/(high[i] - low[i]) for i in range(len(d))]
	newrows = []
	for row in rows:
		d = row.data
		newrow = scaleFunction(d) + [row.match]
		newrows.append(matchrow(newrow))
	return newrows, scaleFunction

def plotAgeMatches(rows):
	x1, y1 = zip(*[(r.data[0], r.data[1]) for r in rows if r.match == 1])
	x2, y2 = zip(*[(r.data[0], r.data[1]) for r in rows if r.match == 0])
	pylab.plot(x1, y1, 'go')
	pylab.plot(x2, y2, 'rx')
	pylab.show()

def yesOrNo(v):
	if v == 'yes': return 1
	if v == 'no': return -1
	return 0

def matchCount(interest1, interest2):
	i1 = interest1.split(':')
	i2 = interest2.split(':')
	count = 0
	for val in i1:
		if val in i2:
			count += 1
	return count

def getLocation(address):
	if address in loc_cache:
		return loc_cache[address]
	url = 'http://maps.googleapis.com/maps/api/geocode/xml?address=' + address.replace(' ', '+')
	data = urllib2.urlopen(url).read()
	doc = parseString(data)
	lat = doc.getElementsByTagName('lat')[0].firstChild.nodeValue
	lng = doc.getElementsByTagName('lng')[0].firstChild.nodeValue
	loc_cache[address] = (float(lat), float(lng))
	time.sleep(0.2)
	return loc_cache[address]

def haversineDistance(lat1, lng1, lat2, lng2, miles=True):
	R = 3959.0 if miles else 6371.0
	phi1 = math.radians(lat1)
	phi2 = math.radians(lat2)
	deltaphi = math.radians(lat2 - lat1)
	deltalambda = math.radians(lng2 - lng1)
	a = math.sin(deltaphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(deltalambda/2)**2
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
	return R * c

def getMilesDistance(addr1, addr2):
	lat1, lng1 = getLocation(addr1)
	lat2, lng2 = getLocation(addr2)
	return haversineDistance(lat1, lng1, lat2, lng2)

### Linear Classification Methods ###

def linearTrain(rows):
	averages = {}
	counts = {}
	for row in rows:
		cl = row.match
		averages.setdefault(cl, [0.0]*len(row.data))
		counts.setdefault(cl, 0)
		for i in range(len(row.data)):
			averages[cl][i] += float(row.data[i])
		counts[cl] += 1
	for cl, val in averages.iteritems():
		for i in range(len(val)):
			val[i] /= counts[cl]
	return averages

def dotProduct(v1, v2):
	return sum([v1[i]*v2[i] for i in range(len(v1))])

def dpClassify(point, avgs):
	b = (dotProduct(avgs[1], avgs[1]) - dotProduct(avgs[0], avgs[0])) / 2
	y = dotProduct(point, avgs[0]) - dotProduct(point, avgs[1]) + b
	if y > 0: return 0
	else: return 1

### Non linear Classification Methods ###

def rbf(v1, v2, gamma=20):
	l2 = sum([1.0*(v2[i] - v1[i])**2 for i in range(len(v1))])
	return math.exp(-l2*gamma)

def nonlinearClassify(point, rows, offset, gamma=10):
	sum0, sum1, count0, count1 = 0.0, 0.0, 0, 0
	for row in rows:
		if row.match == 0:
			sum0 += rbf(point, row.data, gamma)
			count0 += 1
		else:
			sum1 += rbf(point, row.data, gamma)
			count1 += 1
	y = 1.0 * sum0 / count0 - 1.0 * sum1 / count1 + offset
	if y > 0: return 0
	else: return 1

def getOffset(rows, gamma=10):
	l0, l1 = [], []
	for row in rows:
		if row.match == 0: l0.append(row.data)
		else: l1.append(row.data)
	sum0 = sum([sum([rbf(v1, v2, gamma) for v1 in l0]) for v2 in l0])
	sum1 = sum([sum([rbf(v1, v2, gamma) for v1 in l1]) for v2 in l1])
	return 1.0*sum1/(len(l1)**2) - 1.0*sum0/(len(l0)**2)


if __name__ == '__main__':

	# agesonly = loadmatch('agesonly.csv', allnum=True)
	# offset = getOffset(agesonly)
	# print nonlinearClassify([30, 30], agesonly, offset)
	# print nonlinearClassify([30, 25], agesonly, offset)
	# print nonlinearClassify([25, 40], agesonly, offset)
	# print nonlinearClassify([48, 20], agesonly, offset)

	numericalSet = loadNumerical('matchmaker.csv')
	scaleDataSet, scaleFunction = scaledata(numericalSet)
	# offset = getOffset(scaleDataSet)
	# print nonlinearClassify(scaleFunction(numericalSet[0].data), scaleDataSet, offset)
	# print numericalSet[0].match
	# print nonlinearClassify(scaleFunction(numericalSet[1].data), scaleDataSet, offset)
	# print numericalSet[1].match
	# print nonlinearClassify(scaleFunction(numericalSet[2].data), scaleDataSet, offset)
	# print numericalSet[2].match
	# newrow = [28.0, -1, -1, 26.0, -1, 1, 2, 0.8]
	# print nonlinearClassify(scaleFunction(newrow), scaleDataSet, offset)
	# newrow = [28.0, -1, 1, 26.0, -1, 1, 2, 0.8]
	# print nonlinearClassify(scaleFunction(newrow), scaleDataSet, offset)

	answers, inputs = [r.match for r in scaleDataSet], [r.data for r in scaleDataSet]
	param = svm_parameter('-t 2')
	prob = svm_problem(answers, inputs)
	m = svm_train(prob, param)
	print m
	print ''
	newrow = [[28.0, -1, -1, 26.0, -1, 1, 2, 0.8]]
	print svm_predict([0]*len(newrow), newrow, m)
	newrow = [[28.0, -1, 1, 26.0, -1, 1, 2, 0.8]]
	print svm_predict([0]*len(newrow), newrow, m)
	









