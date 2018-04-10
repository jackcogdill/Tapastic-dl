import os, sys, urllib, urllib2, console, re
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) \
	AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.97 Safari/537.11'
header = { 'User-Agent': user_agent }
(width, height) = console.getTerminalSize()

def getPage(url):
	req = urllib2.Request(url, None, header)
	return urllib2.urlopen(req).read()

def getSoup(url):
	return BeautifulSoup(getPage(url))

def clrlns(num_lines):
	num_lines += 1
	def moveCursorUp(n):
		print '\033[%sA' % n
	moveCursorUp(num_lines)
	for i in range(num_lines -1): print ' ' * width
	moveCursorUp(num_lines)

def fix_url(s):
	patt = '(%\w\w)'
	for quote in re.findall(patt, s):
		s = s.replace(quote, urllib2.unquote(quote))
	return s

def fixdir(fdir):
	for c in '/?<>\:*|"':
		fdir = fdir.replace(c, '-')
	return fdir

def downloadb(url, filename=''):
	def fileName(url):
		return url[(url.rindex('/') +1):]
	if filename == '': filename = fileName(fix_url(url))
	filename = fixdir(filename)
	url = urllib.urlopen(url).geturl()

	def byte_convert(b):
		n, b = 0, float(b)
		while b / 1024 >= 1:
			b = b / 1024
			n += 1
		return '%.2f%s' % (b, 'BKMGT'[n])

	def dlProgress(am, bls, ts):
		per = am * bls * 100.0 / ts
		if per > 100: per = 100.0
		s = '\r%s[%s]' % (('%.1f%%' % per).ljust(6, ' '), (('=' * int(per * 75 / 100))[:-1]+'>').ljust(75, ' '))
		s += ' Size: ' + byte_convert(ts)
		sys.stdout.write(s + ' ' * (width - len(s)))
		sys.stdout.flush()

	try:
		urllib.urlretrieve(url, filename, reporthook=dlProgress)
		print
	except:
		if os.path.isfile(filename): os.remove(filename)
		return False

def main():
	url_ = raw_input('Enter series: ')
	url_ = 'https://tapastic.com/series/' + url_

	mg = url_.split('/')[-1]
	if not os.path.isdir(mg): os.mkdir(mg)
	os.chdir(mg)

	text_ = getPage(url_)
	ep_num = re.findall('data-episode-id="([0-9]+)"', text_)[0]
	url = 'https://tapastic.com/episode/%s' % ep_num

	text = getPage(url)
	for j, ep in enumerate(re.findall('"id":([0-9]+),', text)):
		link = 'https://tapastic.com/episode/%s' % ep
		print 'Downloading episode %s...' % ep

		soup = getSoup(link)
		L = []
		for x in soup.findAll('img'):
			if x.has_key('class'):
				if x['class'] == 'art-image':
					L.append(x['src'])

		for i, item in enumerate(L):
			fname = os.path.basename(item)
			fname = fixdir(fname)
			fname = '%02d_%02d_' % (j, i) + fname
			if not os.path.isfile(fname):
				downloadb(item, filename=fname)

main()
