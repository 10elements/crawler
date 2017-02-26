__author__ = 'Dimitri Zhang'
import urllib.request as urlreq
import re
from bs4 import BeautifulSoup
import os
import os.path
import threading
from queue import Queue
from multiprocessing.dummy import Pool

class Downloader(threading.Thread):
	def __init__(self, queue):
		threading.Thread.__init__(self)
		self.queue = queue

	def run(self):
		while True:
			msg = self.queue.get()
			if isinstance(msg, str) and msg == 'quit':
				break
			fdir, url = msg
			print('downloading %s' %url)
			with open(fdir, 'wb') as f:
				f.write(urlreq.urlopen(url).read())
			print('%s downloaded' %url)
			self.queue.task_done()

def crawling(url):
	homDir = '.'
	if not os.path.exists(homDir):
		os.mkdir(homDir)
	stack = [url]
	# reg_1 = re.compile(r'[A-Z0-9]+/')
	# reg_2 = re.compile(r'[A-Z0-9]+\.[A-Z0-9]+')

	downloaders = []
	queue = Queue()
	for i in range(8):
		dl = Downloader(queue)
		dl.start()
		downloaders.append(dl)

	while len(stack) != 0:# DFS
		topUrl = stack.pop()
		urltoken = topUrl.split('/')
		fdir = homDir + '/' + topUrl[topUrl.find('Android%20Programming/'):]#dir in file system
		if urltoken[-1] == '':#if path
			if not os.path.exists(fdir):
				os.mkdir(fdir)
			response = urlreq.urlopen(topUrl)
			soup = BeautifulSoup(response.read(), 'lxml')
			for link in soup.find_all('a'):
				href = link.get('href')
				if not href.startswith('/~vkepuska') and not href.startswith('?'):
					stack.append(topUrl + link.get('href'))
		else:
			queue.put((fdir, topUrl))
	for i in range(8):
		queue.put('quit')
	for dl in downloaders:
		dl.join()

def nextURL(url):
	homDir = '.'
	if not os.path.exists(homDir):
		os.mkdir(homDir)
	stack = [url]
	while len(stack) != 0:
		topUrl = stack.pop()
		urltoken = topUrl.split('/')
		fdir = homDir + '/' + topUrl[topUrl.find('Android%20Programming/'):]#dir in file system
		if urltoken[-1] == '':#if path
			if not os.path.exists(fdir):
				os.mkdir(fdir)
			response = urlreq.urlopen(topUrl)
			soup = BeautifulSoup(response.read(), 'lxml')
			for link in soup.find_all('a'):
				href = link.get('href')
				if not href.startswith('/~vkepuska') and not href.startswith('?'):
					stack.append(topUrl + link.get('href'))
		else:
			print(fdir)
			yield (fdir, topUrl)

def download(val):
	fdir, url = val
	print('downloading %s' %url)
	with open(fdir, 'wb') as f:
		f.write(urlreq.urlopen(url).read())
	print('%s downloaded' %url)

def parallelCrawling(url):
	threadPool = Pool(12)
	threadPool.map(download, nextURL(url))
	threadPool.close()
	threadPool.join()



def main():
	crawling('http://my.fit.edu/~vkepuska/Android%20Programming/')
	# parallelCrawling('http://my.fit.edu/~vkepuska/Android%20Programming/')
	
if __name__ == '__main__':
	main()