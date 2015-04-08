from math import sqrt
import random

critics = {'Jinfeng Huang': {'Machine Learning': 4.5, 'Computer Systems': 5.0, 'Materials Chemistry': 4.0, 'Algorithm Analysis': 3.5, 'Nanoscience': 4.0, 'Biomaterials': 3.5}, \
		   'Xinxing Jiang': {'Machine Learning': 4.5, 'Materials Chemistry': 1.0, 'Algorithm Analysis': 4.5, 'Nanoscience': 1.0, 'Biomaterials': 1.0}, \
		   'Yuchun Yin': {'Machine Learning': 4.5, 'Materials Chemistry': 4.0, 'Algorithm Analysis': 2.0, 'Nanoscience': 4.0, 'Biomaterials': 4.0}, \
		   'Jason Lin': {'Computer Systems': 2.0, 'Materials Chemistry': 4.5, 'Algorithm Analysis': 1.5, 'Nanoscience': 4.5, 'Biomaterials': 3.0}, \
		   'Ziyu Jin': {'Computer Systems': 1.0, 'Materials Chemistry': 3.0, 'Algorithm Analysis': 1.0, 'Nanoscience': 3.0, 'Biomaterials': 3.0}, \
		   'Xijia Duan': {'Computer Systems': 1.0, 'Materials Chemistry': 3.0, 'Algorithm Analysis': 2.5, 'Nanoscience': 4.5, 'Biomaterials': 3.0}, \
		   }

def eculid_distance(prefs, person1, person2):
	shared_item = {}
	for item in prefs[person1]:
		if item in prefs[person2]:
			shared_item[item] = 1
	if len(shared_item) == 0:
		return 0

	sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2) for item in prefs[person1] if item in prefs[person2]])
	return 1/(1 + sqrt(sum_of_squares))

def pearson_correlation(prefs, person1, person2):
	shared_item = {}
	for item in prefs[person1]:
		if item in prefs[person2]:
			shared_item[item] = 1

	n = len(shared_item)
	if n == 0: return 0

	sum_person1 = sum([prefs[person1][item] for item in shared_item])
	sum_person2 = sum([prefs[person2][item] for item in shared_item])
	sum_person1_square = sum([pow(prefs[person1][item], 2) for item in shared_item])
	sum_person2_square = sum([pow(prefs[person2][item], 2) for item in shared_item])
	sum_multiply = sum([prefs[person1][item]*prefs[person2][item] for item in shared_item])

	upper = sum_multiply - (sum_person1 * sum_person2 / n)
	lower = sqrt((sum_person1_square - (pow(sum_person1, 2) / n)) * (sum_person2_square - (pow(sum_person2, 2) / n)))

	if lower == 0: return 0
	return upper/lower

def top_matches(prefs, person, sim = pearson_correlation):
	scores = [(sim(prefs, person, other), other) for other in prefs if other != person]
	scores.sort()
	scores.reverse()
	return scores

def get_recommendations(prefs, person, sim = pearson_correlation):
	totals = {}
	simSums = {}
	for other in prefs:
		if other == person: continue
		sims = (1 + sim(prefs, person, other)) / 2
		for item in prefs[other]:
			totals.setdefault(item, 0)
			totals[item] += prefs[other][item]*sims
			simSums.setdefault(item, 0)
			simSums[item] += sims

	rankings = [(t/simSums[item], item) for item, t in totals.items()]
	rankings.sort()
	rankings.reverse()
	return rankings

def transformPrefs(prefs):
	res = {}
	for person in prefs:
		for item in prefs[person]:
			res.setdefault(item, {})
			res[item][person] = prefs[person][item]
	return res

def calculateSimilarItems(prefs, n=10):
	res = {}
	itemPrefs = transformPrefs(prefs)
	status = 0
	for item in itemPrefs:
		status += 1
		if status % 100 == 0:
			print '%d / %d' % (status, len(itemPrefs))
		scores = top_matches(itemPrefs, item, eculid_distance)[0:n]
		res[item] = scores
	return res

def getRecommendedItems(prefs, itemMatch, user):
	userRatings = prefs[user]
	scores = {}
	totalSim = {}
	for (item, rating) in userRatings.iteritems():
		for (similarity, item2) in itemMatch[item]:
			if item2 in userRatings:
				continue
			scores.setdefault(item2, 0)
			scores[item2] += similarity * rating
			totalSim.setdefault(item2, 0)
			totalSim[item2] += similarity
	rankings = [(item, score/totalSim[item]) for (item, score) in scores.iteritems()]
	rankings = sorted(rankings, key=lambda x: -x[1])
	return rankings

def loadMovieLens(path='./ml-100k/'):
	movies = {}
	for line in open(path+'u.item'):
		(movieid, title) = line.split('|')[0:2]
		movieid = int(movieid)
		movies[movieid] = title
	prefs = {}
	for line in open(path+'u.data'):
		(user, movieid, rating, ts) = line.split('\t')
		user = int(user)
		movieid = int(movieid)
		prefs.setdefault(user, {})
		prefs[user][movies[movieid]] = float(rating)
	return prefs

if __name__ == '__main__':
	prefs = loadMovieLens()
	user = random.randint(0, 100)
	print user
	print get_recommendations(prefs, user, eculid_distance)[0:10]
	itemsim = calculateSimilarItems(prefs)
	print getRecommendedItems(prefs, itemsim, user)[0:10]
























