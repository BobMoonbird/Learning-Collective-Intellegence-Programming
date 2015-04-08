import math, random
import Image, ImageDraw
import sys

def readfile(filename):
	lines = [line for line in open(filename, 'r')]
	colnames = lines[0].strip().split('\t')[1:]
	rownames = []
	data = []
	for line in lines[1:]:
		info = line.strip().split('\t')
		rownames.append(info[0])
		data.append([float(num) for num in info[1:]])
	return rownames, colnames, data

def pearson_distance(list1, list2):
	n = len(list1)
	if n == 0:
		return 0.01
	sum1 = sum(list1)
	sum2 = sum(list2)
	productSum = sum([list1[i]*list2[i] for i in range(n)])
	squareSum1 = sum([list1[i]*list1[i] for i in range(n)])
	squareSum2 = sum([list2[i]*list2[i] for i in range(n)])
	upper = productSum - 1.0 * sum1 * sum2 / n
	lower1 = math.sqrt(squareSum1 - 1.0 * math.pow(sum1, 2) / n)
	lower2 = math.sqrt(squareSum2 - 1.0 * math.pow(sum2, 2) / n)
	if (lower1 * lower2 == 0):
		return 1
	return 1.0 - upper / (lower1 * lower2)

def jaccard_distance(list1, list2):
	set1, set2, share = 0, 0, 0
	for i in range(len(list1)):
		if list1[i] != 0:
			set1 += 1
		if list2[i] != 0:
			set2 += 1
		if list1[i] != 0 and list2[i] != 0:
			share += 1
	if set1 + set2 - share == 0:
		return 1.0
	return 1.0 - 1.0 * share / (set1 + set2 - share)

def eculid_distance(list1, list2):
	n = len(list1)
	sum_of_squares = sum([pow(list1[i] - list2[i], 2) for i in range(n)])
	return 1/(1 + math.sqrt(sum_of_squares))

class bicluster:
	def __init__(self, vec, left=None, right=None, distance=0.0, identity=None):
		self.left = left
		self.right = right
		self.vec = vec
		self.identity = identity
		self.distance = distance

def hcluster(rows, distance=pearson_distance):
	distances = {}
	currID = -1
	clusters = [bicluster(rows[i], identity=i) for i in range(len(rows))]
	while len(clusters) > 1:
		lowestPair = (0, 1)
		closest = distance(clusters[0].vec, clusters[1].vec)
		for i in range(len(clusters)):
			for j in range(i+1, len(clusters)):
				if (clusters[i].identity, clusters[j].identity) not in distances:
					distances[(clusters[i].identity, clusters[j].identity)] = distance(clusters[i].vec, clusters[j].vec)
				currDist = distances[(clusters[i].identity, clusters[j].identity)]
				if currDist < closest:
					closest = currDist
					lowestPair = (i, j)
		mergevec = [clusters[lowestPair[0]].vec[i] * clusters[lowestPair[1]].vec[i] / 2.0 for i in range(len(clusters[0].vec))]
		newcluster = bicluster(mergevec, left=clusters[lowestPair[0]], right=clusters[lowestPair[1]], distance=closest, identity=currID)
		currID -= 1
		del clusters[lowestPair[1]]
		del clusters[lowestPair[0]]
		clusters.append(newcluster)
	return clusters[0]

def printclusters(cluster, labels=None, n=0):
	for i in range(n): 
		print '\t',
	if cluster.identity < 0:
		print '-'
	else:
		if labels == None:
			print cluster.identity
		else:
			print labels[cluster.identity]
	if cluster.left != None:
		printclusters(cluster.left, labels=labels, n=n+1)
	if cluster.right != None:
		printclusters(cluster.right, labels=labels, n=n+1)

def getHeight(cluster):
	if cluster.left == None and cluster.right == None:
		return 1
	else:
		return getHeight(cluster.left) + getHeight(cluster.right)

def getDepth(cluster):
	if cluster.left == None and cluster.right == None:
		return 0
	else:
		return max(getDepth(cluster.left), getDepth(cluster.right)) + cluster.distance

def drawDendrogram(cluster, labels, jpeg='clusters.jpg'):
	h = getHeight(cluster) * 20
	w = 1200
	d = getDepth(cluster)
	scaling = float(w - 150) / d
	img = Image.new('RGB', (w, h), (255, 255, 255))
	draw = ImageDraw.Draw(img)
	draw.line((0, h/2, 10, h/2), fill=(255, 0, 0))
	drawnode(draw, cluster, 10, (h/2), scaling, labels)
	img.save(jpeg, 'JPEG')

def drawnode(draw, cluster, x, y, scaling, labels):
	if cluster.identity < 0:
		h1 = getHeight(cluster.left) * 20
		h2 = getHeight(cluster.right) * 20
		top = y - (h1 + h2)/2
		bottom = y + (h1 + h2)/2
		lineLen = cluster.distance * scaling
		draw.line((x, top+h1/2, x, bottom-h2/2), fill=(255, 0, 0))
		draw.line((x, top+h1/2, x+lineLen, top+h1/2), fill=(255, 0, 0))
		draw.line((x, bottom-h2/2, x+lineLen, bottom-h2/2), fill=(255, 0, 0))
		drawnode(draw, cluster.left, x + lineLen, top + h1/2, scaling, labels)
		drawnode(draw, cluster.right, x + lineLen, bottom - h2/2, scaling, labels)
	else:
		draw.text((x+5, y-7), labels[cluster.identity], (0, 0, 0))

def rotateMatrix(data):
	newdata = []
	for i in range(len(data[0])):
		newrow = [data[j][i] for j in range(len(data))]
		newdata.append(newrow)
	return newdata

def kcluster(rows, distance=pearson_distance, k=4):
	ranges = [(min([row[i] for row in rows]), max([row[i] for row in rows])) for i in range(len(rows[0]))]
	clusters = [[(random.random() * (ranges[i][1] - ranges[i][0]) + ranges[i][0]) for i in range(len(rows[0]))] for _ in range(k)]
	lastmatches = None
	for t in range(100):
		print 'Iteration %d' % t
		bestmatches = [[] for i in range(k)]
		for j in range(len(rows)):
			row = rows[j]
			bestmatch = 0
			for i in range(k):
				d = distance(clusters[i], row)
				if d < distance(clusters[bestmatch], row):
					bestmatch = i
			bestmatches[bestmatch].append(j)
		if bestmatches == lastmatches:
			break
		lastmatches = bestmatches
		for i in range(k):
			avgs = [0.0] * len(rows[0])
			if len(bestmatches[i]) > 0:
				for rowid in bestmatches[i]:
					for m in range(len(rows[rowid])):
						avgs[m] += rows[rowid][m]
				for j in range(len(avgs)):
					avgs[i] /= len(bestmatches[i])
				clusters[i] = avgs
	return bestmatches

def scaledown(data, distance=pearson_distance, rate=0.01):
	n = len(data)
	realDistance = [[distance(data[i], data[j]) for j in range(n)] for i in range(n)]
	outerSum = 0
	loc = [[random.random(), random.random()] for i in range(n)]
	fakeDistance = [[0.0 for j in range(n)] for i in range(n)]
	lastError = None
	for m in range(0, 1000):
		for i in range(n):
			for j in range(n):
				fakeDistance[i][j] = math.sqrt(sum([pow(loc[i][x] - loc[j][x], 2) for x in range(len(loc[i]))]))
		grad = [[0.0, 0.0] for i in range(n)]
		totalError = 0
		for k in range(n):
			for j in range(n):
				if j == k:
					continue
				error = (fakeDistance[j][k] - realDistance[j][k]) / realDistance[j][k]
				grad[k][0] += ((loc[k][0] - loc[j][0]) / fakeDistance[j][k]) * error
				grad[k][1] += ((loc[k][1] - loc[j][1]) / fakeDistance[j][k]) * error
				totalError += abs(error)
		if lastError and lastError < totalError:
			break
		lastError = totalError
		for k in range(n):
			loc[k][0] -= rate * grad[k][0]
			loc[k][1] -= rate * grad[k][1]
	return loc

def draw2D(data, labels, jpeg, cluster=None, k=0):
	image = Image.new('RGB', (2000, 2000), (255, 255, 255))
	draw = ImageDraw.Draw(image)
	colors = None
	if cluster != None and k > 0:
		colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
		if k > 6:
			colors += [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for _ in range(k - 6)]
	for i in range(len(data)):
		x = (data[i][0] + 0.5) * 1000
		y = (data[i][1] + 0.5) * 1000
		draw.text((x, y), labels[i], (0, 0, 0))
		if colors:
			color = (0, 0, 0)
			for j in range(k):
				if i in cluster[j]:
					color = colors[j]
					break
			r = 10
			draw.ellipse((x-r, y-r, x+r, y+r), color)
	image.save(jpeg, 'JPEG')


if __name__ == '__main__':
	filename = raw_input('Enter the name of data file: ')
	blognames, words, data = readfile(filename)
	outputImage = raw_input('Enter the name of output image file: ')
	if (len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == '-h')):	
		cluster = hcluster(data, distance=jaccard_distance)
		drawDendrogram(cluster, blognames, jpeg=outputImage)
	elif (len(sys.argv) >= 3 and sys.argv[1] == '-k'):
		k = int(sys.argv[2])
		cluster = kcluster(data, distance=pearson_distance, k=k)
		for i in range(k):
			print 'cluster ' + str(i + 1) + ':\t'
			for j in cluster[i]:
				print blognames[j] + ', ',
			print '\n'
		if (len(sys.argv) >= 4 and sys.argv[3] == '-2d'):
			coordinates = scaledown(data, distance=pearson_distance)
			draw2D(coordinates, blognames, jpeg=outputImage, cluster=cluster, k=k)
	elif (len(sys.argv) >= 2 and sys.argv[1] == '-2d'):
		coordinates = scaledown(data)
		draw2D(coordinates, blognames, jpeg=outputImage)

