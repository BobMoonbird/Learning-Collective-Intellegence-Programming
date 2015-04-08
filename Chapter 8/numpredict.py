import random, math, functools
import optimization
import pylab

weightDomain = [(0, 20)] * 4

def winePrice(rating, age):
	peakAge = rating - 50
	price = rating / 2
	if age > peakAge:
		price *= 5 - (age - peakAge)
	else:
		price *= 5 * ((age + 1) / peakAge)
	return max(price, 0)

def wineSet():
	rows = []
	for i in range(300):
		age = random.random() * 50
		rating = random.random() * 50 + 50
		price = winePrice(rating, age)
		price *= random.random() * 0.4 + 0.8
		rows.append({'input': (rating, age), 'result': price})
	return rows

def wineSet2():
	rows = []
	for i in range(300):
		age = random.random() * 50
		rating = random.random() * 50 + 50
		aisle = 1.0 * random.randint(1, 20)
		bottlesize = [375.0, 750.0, 1500.0, 3000.0][random.randint(0, 3)]
		price = winePrice(rating, age)
		price *= bottlesize/750
		price *= (random.random() * 0.2 + 0.9)
		rows.append({'input': (rating, age, aisle, bottlesize), 'result': price})
	return rows

def wineSet3():
	rows = wineSet()
	for row in rows:
		if random.random() < 0.5:
			row['result'] *= 0.5
	return rows

def eculidean(v1, v2):
	d = 0.0
	for i in range(len(v1)):
		d += (v2[i] - v1[i])**2
	return math.sqrt(d)

def getDistances(data, vec):
	distList = []
	for i in range(len(data)):
		vec2 = data[i]['input']
		distList.append((eculidean(vec, vec2), i))
	distList.sort()
	return distList

def kNNEstimate(data, vec, k=3):
	distList = getDistances(data, vec)
	avg = 0.0
	for i in range(k):
		index = distList[i][1]
		avg += data[index]['result']
	return avg/k

def inverseWeight(dist, num=1.0, const=0.1):
	return num/(dist+const)

def substractWeight(dist, const=1.0):
	if dist > const: return 0
	else: return const - dist

def gaussian(dist, sigma=10.0):
	return math.exp(-dist**2/(2*sigma**2))

def weightedKNNEstimate(data, vec, k=3, weightFunction=gaussian):
	distList = getDistances(data, vec)
	avg = 0.0
	totalWeight = 0.0
	for i in range(k):
		index = distList[i][1]
		weight = gaussian(distList[i][0])
		avg += weight * data[index]['result']
		totalWeight += weight
	return avg/totalWeight

def divideData(data, test=0.05):
	trainingSet = []
	testSet = []
	for row in data:
		if random.random() < test:
			testSet.append(row)
		else:
			trainingSet.append(row)
	return trainingSet, testSet

def testAlgorithm(algorithmFunction, trainingSet, testSet):
	error = 0.0
	for row in testSet:
		guess = algorithmFunction(trainingSet, row['input'])
		error += (row['result'] - guess)**2
	return error/len(testSet)

def crossValidate(algorithmFunction, data, trials=100, test=0.05):
	error = 0.0
	for _ in range(trials):
		trainingSet, testSet = divideData(data, test)
		error += testAlgorithm(algorithmFunction, trainingSet, testSet)
	return error/trials

def rescale(data, scale):
	scaleddata = []
	for row in data:
		scaledrow = [scale[i]*row['input'][i] for i in range(len(scale))]
		scaleddata.append({'input': scaledrow, 'result': row['result']})
	return scaleddata

def createCostFunction(algorithmFunction, data):
	def costFunction(scale):
		scaleddata = rescale(data, scale)
		return crossValidate(algorithmFunction, scaleddata, trials=10)
	return costFunction

def probGuess(data, vec, low, high, k=5, weightFunction=gaussian):
	distList = getDistances(data, vec)
	nWeight = 0.0
	tWeight = 0.0
	for i in range(k):
		dist = distList[i][0]
		index = distList[i][1]
		weight = weightFunction(dist)
		val = data[i]['result']
		if val >= low and val <= high:
			nWeight += weight
		tWeight += weight
	if tWeight == 0: return 0
	return nWeight/tWeight

def cumulativeGraph(data, vec, high, k=5, weightFunction=gaussian):
	t1 = pylab.arange(0.0, high, 0.1)
	cprob = pylab.array([probGuess(data, vec, 0, v, k, weightFunction) for v in t1])
	pylab.plot(t1, cprob)
	pylab.show()

def probabilityGraph(data, vec, high, k=5, weightFunction=gaussian, ss=1.0):
	t1 = pylab.arange(0.0, high, 0.1)
	probs = [probGuess(data, vec, v, v+0.1, k, weightFunction) for v in t1]
	smoothed = []
	for i in range(len(probs)):
		sv = 0.0
		for j in range(len(probs)):
			dist = abs(i - j) * 0.1
			weight = gaussian(dist, sigma=ss)
			sv += weight * probs[j]
		smoothed.append(sv)
	smoothed = pylab.array(smoothed)
	pylab.plot(t1, smoothed)
	pylab.show()


if __name__ == '__main__':
	data = wineSet3()
	probabilityGraph(data, (1, 1), 120)









	