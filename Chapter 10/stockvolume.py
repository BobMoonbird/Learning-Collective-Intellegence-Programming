import nmf, urllib2, numpy as np

StockTickers = ['YHOO', 'GOOG', 'AAPL', 'MSFT', 'AMZN', 'TWTR', 
				'FB', 'LNKD', 'BABA', 'BIDU', 'GE', 'F']

def downloadFinanceData(shortest=300):
	prices = {}
	dates = None
	for ticker in StockTickers:
		url = 'http://ichart.finance.yahoo.com/table.csv?' +\
			  's=%s&d=3&e=1&f=2015&g=d&a=3&b=1&c=2005' % ticker +\
			  '&ignore=.csv'
		rows = urllib2.urlopen(url).readlines()
		prices[ticker] = [float(row.split(',')[5]) for row in rows[1:] if row.strip() != '']
		if len(prices[ticker]) < shortest: shortest = len(prices[ticker])
		if not dates:
			dates = [row.split(',')[0] for row in rows[1:] if row.strip() != '']
	matrix = [[prices[StockTickers[i]][j] for i in range(len(StockTickers))] for j in range(shortest)]
	return np.matrix(matrix), dates, shortest

def showResults(w, h, dates, shortest, topStock=12, topDate=3):
	for i in range(np.shape(h)[0]):
		print 'Feature %d' % i
		stocklist = [(h[i, j], StockTickers[j]) for j in range(len(StockTickers))]
		stocklist = sorted(stocklist, reverse=True)
		for j in range(topStock):
			print stocklist[j]
		print ''
		datelist = [(w[j, i], j) for j in range(shortest)]
		datelist = sorted(datelist, reverse=True)
		print [(date[0], dates[date[1]]) for date in datelist[:topDate]]
		print ''

if __name__ == '__main__':
	m, dates, shortest = downloadFinanceData()
	w, h = nmf.factorize(m)
	showResults(w, h, dates, shortest)
