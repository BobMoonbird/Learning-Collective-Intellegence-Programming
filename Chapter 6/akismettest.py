import akismet

defaultkey = ""
pageurl = "https://wordpress.org/news/"
defaultagent = "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2) Gecko/20100115 Firefox/3.6"

def isspam(comment, author, ipaddress, agent=defaultagent, apikey=defaultkey):
	try:
		valid = akismet.verify_key(apikey, pageurl)
		if valid:
			return akismet.comment_check(apikey, pageurl, ipaddress, agent, comment_content=comment, comment_author_email=author, comment_type="comment")
		else:
			print "Invalid key"
			return False
	except akismet.AkismetError, e:
		print e.response, e.statuscode
		return False

if __name__ == '__main__':
	msg = "Make Money Fast! Online Casino!"
	print isspam(msg, '105472@qq.com', '66.155.40.249')