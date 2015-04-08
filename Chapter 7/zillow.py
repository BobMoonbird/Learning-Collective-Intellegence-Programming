import xml.dom.minidom
import urllib2
import treepredict

ZWSID = ''

def getAddressData(address, city):
	escad = address.replace(' ', '+')
	url = 'http://www.zillow.com/webservice/GetDeepSearchResults.htm?'
	url += 'zws-id=%s&address=%s&citystatezip=%s' % (ZWSID, escad, city)
	doc = xml.dom.minidom.parseString(urllib2.urlopen(url).read())
	code = doc.getElementsByTagName('code')[0].firstChild.data

	if code != '0': 
		print 'Code Error!'
		return None
	try:
		zipcode = doc.getElementsByTagName('zipcode')[0].firstChild.data
		use = doc.getElementsByTagName('useCode')[0].firstChild.data
		year = doc.getElementsByTagName('yearBuilt')[0].firstChild.data
		bath = doc.getElementsByTagName('bathrooms')[0].firstChild.data
		bed = doc.getElementsByTagName('bedrooms')[0].firstChild.data
		rooms = doc.getElementsByTagName('totalRooms')[0].firstChild.data
		price = doc.getElementsByTagName('amount')[0].firstChild.data
	except:
		print 'Error!'
		return None

	return (str(zipcode), str(use), int(year), float(bath), int(bed), int(rooms), int(price))

def getPriceList(filename):
	pricelist = []
	for line in open(filename):
		data = getAddressData(line.strip(), 'Cambridge,MA')
		if data != None: pricelist.append(data)
	return pricelist

if __name__ == '__main__':
	housedata = getPriceList('addresslist.txt')
	housetree = treepredict.buildtree(housedata, scoreFunction=treepredict.variance)
	treepredict.drawTree(housetree, 'housetree.jpg')
