import httplib, urllib2
from xml.dom.minidom import parse, parseString, Node
import numpredict

devKey = ''
appKey = ''
certKey = ''
userToken = ''
serverURL = 'api.ebay.com'

def getHeaders(apicall, siteID='0', compatibilityLevel='433'):
	headers = {'X-EBAY-API-COMPATIBILITY-LEVEL': compatibilityLevel,
			   'X-EBAY-API-DEV-NAME': devKey,
			   'X-EBAY-API-APP-NAME': appKey,
			   'X-EBAY-API-CERT-NAME': certKey,
			   'X-EBAY-API-CALL-NAME': apicall,
			   'X-EBAY-API-SITEID': siteID,
			   'Content-Type': 'text/xml'}
	return headers

def sendRequest(apicall, xmlparameters):
	connection = httplib.HTTPSConnection(serverURL)
	connection.request('POST', '/ws/api.dll', xmlparameters, getHeaders(apicall))
	response = connection.getresponse()
	data = None
	if response.status != 200:
		print 'Error sending request: ' + response.reason
	else:
		data = response.read()
		connection.close
	return data

def getSingleValue(node, tag):
	nl = node.getElementsByTagName(tag)
	if len(nl) > 0:
		tagNode = nl[0]
		if tagNode.hasChildNodes():
			return tagNode.firstChild.nodeValue
	return '-1'

def doSearch(query, categoryID=None, page=1):
	url = "http://svcs.ebay.com/services/search/FindingService/v1?" +\
		  "SECURITY-APPNAME=" + appKey +\
		  "&OPERATION-NAME=findItemsAdvanced" +\
		  "&SERVICE-VERSION=1.0.0&RESPONSE-DATA-FORMAT=XML" +\
		  "&REST-PAYLOAD=true" +\
		  "&keywords=" + query +\
		  "&paginationInput.entriesPerPage=200" +\
		  "&paginationInput.pageNumber=" + str(page)
	if categoryID != None:
		url += "&categoryId=" + str(categoryID)

	data = urllib2.urlopen(url).read()
	response = parseString(data)
	itemNodes = response.getElementsByTagName('item')
	results = []
	for item in itemNodes:
		itemID = getSingleValue(item, 'itemId')
		itemTitle = getSingleValue(item, 'title')
		itemPrice = getSingleValue(item, 'currentPrice')
		itemEnds = getSingleValue(item, 'endTime')
		results.append((itemID, itemTitle, itemPrice, itemEnds))
	return results

def getCategory(query='', parentID=None, siteID='0'):
	lquery = query.lower()
	xml = "<?xml version='1.0' encoding='utf-8'?>" +\
		  "<GetCategoriesRequest xmlns=\"urn:ebay:apis:eBLBaseComponents\">" +\
		  "<RequesterCredentials><eBayAuthToken>" + userToken + "</eBayAuthToken></RequesterCredentials>" +\
		  "<CategorySiteID>" + siteID + "</CategorySiteID>" +\
  		  "<DetailLevel>ReturnAll</DetailLevel>" +\
  		  "<ViewAllNodes>true</ViewAllNodes>"
	if parentID == None:
		xml += "<LevelLimit>1</LevelLimit>"
	else:
		xml += "<CategoryParent>" + str(parentID) + "</CategoryParent>"
	xml += "</GetCategoriesRequest>"
	data = sendRequest('GetCategories', xml)
	categoryList = parseString(data)
	categoryNodes = categoryList.getElementsByTagName('Category')
	for node in categoryNodes:
		categoryID = getSingleValue(node, 'CategoryID')
		name = getSingleValue(node, 'CategoryName')
		if name.lower().find(lquery) != -1:
			print categoryID, name

def getItem(itemID):
	xml = "<?xml version='1.0' encoding='utf-8'?>" +\
		  "<GetItemRequest xmlns=\"urn:ebay:apis:eBLBaseComponents\">" +\
		  "<RequesterCredentials><eBayAuthToken>" + userToken + "</eBayAuthToken></RequesterCredentials>" +\
		  "<ItemID>" + str(itemID) + "</ItemID>" +\
  		  "<DetailLevel>ItemReturnAttributes</DetailLevel>" +\
  		  "</GetItemRequest>"
  	data = sendRequest('GetItem', xml)
  	response = parseString(data)
  	result = {}
  	result['title'] = getSingleValue(response, 'Title')
  	sellingStatusNode = response.getElementsByTagName('SellingStatus')[0]
  	result['price'] = getSingleValue(sellingStatusNode, 'CurrentPrice')
  	result['bid'] = getSingleValue(sellingStatusNode, 'BidCount')
  	seller = response.getElementsByTagName('Seller')[0]
  	result['feedback'] = getSingleValue(seller, 'FeedbackScore')
  	attributeSet = response.getElementsByTagName('AttributeSet')
  	attributes = {}
  	for attribute in attributeSet:
  		attributeID = attribute.attributes.getNamedItem('attributeID').nodeValue
  		attributeValue = getSingleValue(attribute, 'ValueLiteral')
  		attributes[attributeID] = attributeValue
  	result['attributes'] = attributes
  	return result

def makeLaptopDataSet():
	searchResults = doSearch('laptop', categoryID=51148)
	result = []
	for r in searchResults:
		item = getItem(r[0])
		att = item['attributes']
		try:
			data = (float(att['12']), float(att['26444']), float(att['26446']), float(att['25710']), float(item['feedback']))
			entry = {'input': data, 'result': float(item['price'])}
			result.append(entry)
		except:
			print item['title'] + ' failed'
	return result


if __name__ == '__main__':
	data = makeLaptopDataSet()
	vec = (512, 1000, 14, 40, 1000)
	print numpredict.kNNEstimate(data, vec)

















