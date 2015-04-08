from recommendations import top_matches, get_recommendations
from pydelicious import get_popular, get_userposts, get_urlposts
import random

def initializeUserDict(tag, count=5):
	userDict = {}
	for p1 in get_popular(tag=tag)[0:count]:
		for p2 in get_urlposts(p1['url']):
			user = p2['user']
			userDict[user] = {}
	return userDict

def fillItems(userDict):
	allItems = {}
	for user in userDict:
		for _ in range(3):
			try:
				posts = get_userposts(user)
				break
			except:
				print 'Failed user ' + user + ', retrying...'
				time.sleep(4)
		for post in posts:
			url = post['url']
			userDict[user][url] = 1.0
			allItems[url] = 1
	for ratings in userDict.values():
		for item in allItems:
			if item not in ratings:
				ratings[item] = 0.0

if __name__ == '__main__':
	delusers = initializeUserDict('programming')
	fillItems(delusers)
	user = delusers.keys()[random.randint(0, len(delusers) - 1)]
	print user
	print top_matches(delusers, user)[0:5]
	print get_recommendations(delusers, user)[0:5]




