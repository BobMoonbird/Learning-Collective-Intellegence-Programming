from BeautifulSoup import BeautifulSoup
import urllib2, re, sys

def download(url, tag):
	itemowners = {}
	dropwords = ['a', 'new', 'some', 'more', 'my', 'own', 'the', 'many', 'other', 'another']
	currUser = 0
	c = urllib2.urlopen(url)
	soup = BeautifulSoup(c.read())
	for td in soup('td'):
		if ('style' in dict(td.attrs) and td['style'] == tag):
			items = [a.contents[0].lower().strip() for a in td('a')]
			for item in items:
				txt = ''.join([t for t in item.split() if t not in dropwords])
				if len(txt) < 2:
					continue
				itemowners.setdefault(txt, {})
				itemowners[txt][currUser] = 1
			currUser += 1
	return itemowners, currUser

def writeFile(itemowners, n, filename):
	output = open(filename, 'w')
	output.write('Item')
	for user in range(0, n):
		output.write('\tU%d' % user)
	output.write('\n')
	for item, owners in itemowners.iteritems():
		if len(owners) > 10:
			output.write(item)
			for user in range(n):
				if user in owners:
					output.write('\t1')
				else:
					output.write('\t0')
			output.write('\n')


if __name__ == '__main__':
	url = 'https://wiki.teamfortress.com/wiki/List_of_Self-Made_item_owners'
	tag = 'text-align: center;'
	filename = 'teamfortress.txt'
	itemowners, n = download(url, tag)
	writeFile(itemowners, n, filename)
