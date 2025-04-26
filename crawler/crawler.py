import time
import threading
import traceback

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
    self.parser = Parser(debug=debug)
    self.storer = Storer()
    self.logger = Logger(debug=debug)
    self.limit_lock = threading.Lock()
    self.stop_signal = threading.Event()
    with open("tmp/error.log", "w") as f:
      f.write("Error log initialized.\n")

  def crawl_worker(self):
    """
    Worker function for crawling.
    This method fetches URLs from the frontier, parses the content,
    and stores the results. It continues until the limit is reached or
    there are no more URLs to crawl.
    """
    thread_name = threading.current_thread().name
    empty_retries = 0
    MAX_EMPTY_RETRIES = 5  # Number of times a thread will retry when the queue is empty

    try:
      while not self.stop_signal.is_set():
        with self.limit_lock:
          if self.limit <= 0:
            self.stop_signal.set()
            break

        page_url, depth = self.frontier.get_next_url(self.stop_signal)
        print(f"[{thread_name}] Queue size: {self.frontier._queue.qsize()}")
        
        if page_url is None:
          empty_retries += 1
          if empty_retries >= MAX_EMPTY_RETRIES:
            print(f"[{thread_name}] Exiting after {MAX_EMPTY_RETRIES} empty retries.")
            break
          continue

        fetched_response, timestamp = self.fetcher.fetch(url=page_url)

        if fetched_response is None:
          continue

        html_content, urls, title, first_visible_words = self.parser.parse(html_content=fetched_response.text)

        self.storer.store(url=page_url, html_content=html_content, fetched_response=fetched_response)
        
        self.logger.log(page_url, title, first_visible_words, timestamp)

        self.frontier.add_urls(urls=urls, current_depth=depth)

        empty_retries = 0
        with self.limit_lock:
          self.limit -= 1

    except Exception as e:
      stack_trace = traceback.format_exc()  # Get full stack trace
      with open("tmp/error.log", "a") as f:
        f.write(f"[{thread_name}], Page URL: {page_url}, Error: {stack_trace}\n")

  def crawl(self):
    """
    Starts the crawling process.
    This method initializes the crawling workers and manages the
    crawling process. It creates a thread for each worker and waits
    for all threads to finish.
    """
    threads = []

    for i in range(self.thread_count):
      thread = threading.Thread(target=self.crawl_worker, name=f"CrawlerThread-{i}")
      thread.start()
      threads.append(thread)
    
    while any(t.is_alive() for t in threads):
      active_crawlers = [t for t in threading.enumerate() if t.name.startswith("CrawlerThread")]
      print(f"Active crawler threads: {len(active_crawlers)}, Limit: {self.limit}")
      time.sleep(5)  # Monitor threads every 5 seconds

    for thread in threads:
      thread.join()
    
    self.logger.end_log()
    self.fetcher.close()