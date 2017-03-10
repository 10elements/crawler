# A Simple Web Crawler using python threading, multiprocessing and concurrent.futures

I'm interested in how threading in python works, so I did some analysis and decide to write a simple program using threads. A web crawler
would be a good example to use thread. crawler.py implements a crawler using [threading](https://docs.python.org/3/library/threading.html#module-threading) 
and a crawler using [multiprocessing.dummy](https://docs.python.org/3/library/multiprocessing.html?highlight=multiprocessing#module-multiprocessing.dummy). 
crawler_concurrent.py implements a crawler using [concurrent.futures](https://docs.python.org/3.5/library/concurrent.futures.html#module-concurrent.futures) module.

## Description
I decide to crawl the data at http://my.fit.edu/~vkepuska/Android%20Programming/, in `crawler.py`, first I create a class 
that extends `threading.Thread`, very similar to `Java`, I override the `run` method.
```python
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
```
The `self.queue` member variable is mutil-producer, multi-consumer queue used for safely exchanging information between threads.
It has implemented all the locking semantics, so we don't have do add the `synchronize` keywords manually like we did in the
classic producer-consumer problem written in `Java`.

Now let's move on to the `crawling` method where the crawling operation happens. I manually create a thread pool of 8 threads, 
later you will see that there is a more convenient way of creating thread pool. As you can see the `queue` variable is passed to the
threads in the pool to allow information exchange.
```python
	downloaders = []
	queue = Queue()
	for i in range(8):
		dl = Downloader(queue)
		dl.start()
		downloaders.append(dl)
```
This is a simple Depth-First-Search. Whenever I encounter a resource, I put its url to `queue`. So basically the `crawling`
method is like the producer which continuously produces resource links and the threads in the pool are like consumers who repeatedly
fetch url from the `queue` and download its resource.
```python
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
```
If the task of thread is highly self-contained, then there is a more convenient way to create a thread pool with `concurrent.futures`
module. In `crawler_concurrent.py` I implement a method `crawling`
```python
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
```
As you can see, I can create a thread pool with one line `with concurrent.futures.ThreadPoolExecutor(max_workers = 8) as executor:`,
then in the crawling process whenever I encounter a resource I submit it to `executor` by `executor.submit(download, fdir, url)`, 
`download` is a callable in which the downloading process happens.

What's even more amazing is that by changing `with concurrent.futures.ThreadPoolExecutor(max_workers = 8) as executor:` to 
`with concurrent.futures.ProcessPoolExecutor(max_workers = 8) as executor` I can change my crawler to multiprocessing mode.

Due to the __Global Intepreter Lock__ in python, python thread does not allow real parallelism, which means multiple threads in 
the same process can not be run at the same time. What thread in python support is concurrency, in other words CPU time is 
switched between multiple threads. To achieve parallelism in python, `multiprocessing` module should be used.

## Results


## Built With

* [Python3.5](https://www.python.org)

## Contributing
Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## License

## Acknowledgments

* [Python: what are the differences between the threading and multiprocessing modules?](http://stackoverflow.com/questions/18114285/python-what-are-the-differences-between-the-threading-and-multiprocessing-modul?noredirect=1&lq=1)
* [Threading--Thread-based parallelism](https://docs.python.org/3/library/threading.html#module-threading)
* [multiprocessing--Process-based parallelism](https://docs.python.org/3/library/multiprocessing.html?highlight=multiprocessing#module-multiprocessing)
