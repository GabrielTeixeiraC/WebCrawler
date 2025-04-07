import time
import threading

from .fetcher import Fetcher
from .parser import Parser
from .storer import Storer
from .frontier import Frontier
from utils.logger import Logger

"""
Crawler class for web crawling.
This class is responsible for managing the crawling process, including
fetching URLs, parsing content, and storing results.
"""
class Crawler:
  def __init__(self, seeds: list[str], limit: int, debug: bool, thread_count: int = 100):
    """
    Initializes the Crawler class.
    Args:
      seeds (list[str]): List of seed URLs.
      limit (int): Number of links to be crawled.
      debug (bool): Enable debug mode.
    """
    self.seeds = seeds
    self.limit = limit
    self.thread_count = thread_count
    self.frontier = Frontier(seeds=seeds)
    self.fetcher = Fetcher()
    self.parser = Parser()
    self.storer = Storer()
    self.logger = Logger(debug=debug)
    self.limit_lock = threading.Lock()
    self.frontier_lock = threading.Lock()

  def crawl_worker(self):
    """
    Worker function for crawling.
    This method fetches URLs from the frontier, parses the content,
    and stores the results. It continues until the limit is reached or
    there are no more URLs to crawl.
    """

    while True:
      with self.limit_lock:
        if self.limit <= 0:
          break

      with self.frontier_lock:
        if not self.frontier.has_urls():
          break
        
        ## Get the next URL
        page_url, depth = self.frontier.get_next_url()

      ## Fetch the URL
      fetched_response, timestamp = self.fetcher.fetch(url=page_url)
    
      if fetched_response is None:
        print(f"Failed to fetch {page_url}.")
        continue

      ## Parse the content
      links, title, first_visible_words = self.parser.parse(html_content=fetched_response.text)

      self.logger.log(page_url, title, first_visible_words, timestamp)

      self.frontier.add_links(links=links, current_depth=depth)

      ## Store the fetched fetched_response
      self.storer.store(url=page_url, fetched_response=fetched_response)

      ## Update the limit
      with self.limit_lock:
        self.limit -= 1

  def crawl(self):
    """
    Starts the crawling process.
    This method initializes the crawling workers and manages the
    crawling process. It creates a thread for each worker and waits
    for all threads to finish.
    """
    threads = []

    for _ in range(self.thread_count):
      thread = threading.Thread(target=self.crawl_worker)
      thread.start()
      threads.append(thread)

    for thread in threads:
      thread.join()
    
    self.logger.end_log()
    self.fetcher.close()