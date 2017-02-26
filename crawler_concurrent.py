import urllib.request as urlreq
import re
from bs4 import BeautifulSoup
import os
import os.path
import concurrent.futures

def download(fdir, url):
	print('downloading %s' %url)
	with open(fdir, 'wb') as f:
		f.write(urlreq.urlopen(url).read())
	print('%s downloaded' %url)

def crawling(url):
	homDir = '.'
	if not os.path.exists(homDir):
		os.mkdir(homDir)
	stack = [url]
	with concurrent.futures.ThreadPoolExecutor(max_workers = 8) as executor:
		while len(stack) != 0:# DFS
			topUrl = stack.pop()
			urltoken = topUrl.split('/')
			fdir = homDir + '/' + topUrl[topUrl.find('Android%20Programming/'):]#dir in file system
			if urltoken[-1] == '':#if path
				print(topUrl)
				if not os.path.exists(fdir):
					os.mkdir(fdir)
				response = urlreq.urlopen(topUrl)
				soup = BeautifulSoup(response.read(), 'lxml')
				for link in soup.find_all('a'):
					href = link.get('href')
					if not href.startswith('/~vkepuska') and not href.startswith('?'):
						stack.append(topUrl + link.get('href'))
			else:
				executor.submit(download, fdir, url)

if __name__ == '__main__':
	crawling('http://my.fit.edu/~vkepuska/Android%20Programming/')
