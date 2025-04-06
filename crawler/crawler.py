import time

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
  def __init__(self, seeds: list[str], limit: int, debug: bool):
    """
    Initializes the Crawler class.
    Args:
      seeds (list[str]): List of seed URLs.
      limit (int): Number of links to be crawled.
      debug (bool): Enable debug mode.
    """
    self.seeds = seeds
    self.limit = limit
    self.frontier = Frontier(seeds, debug)
    self.fetcher = Fetcher()
    self.parser = Parser()
    self.storer = Storer()
    self.logger = Logger(debug=debug)

  def crawl(self):
    """
    Starts the crawling process.
    This method fetches URLs from the frontier, parses the content,
    and stores the results. It continues until the limit is reached or
    there are no more URLs to crawl.
    """

    while self.frontier.has_urls() and self.limit > 0:
      ## Get the next URL
      page_url = self.frontier.get_next_url()
      
      timestamp = int(time.time())
      ## Fetch the URL
      fetched_response = self.fetcher.fetch(page_url)

      if fetched_response is None:
        print(f"Failed to fetch {page_url}.")
        continue
      
      ## Parse the content
      links, title, first_visible_words = self.parser.parse(fetched_response.text)

      self.logger.log(page_url, title, first_visible_words, timestamp)

      self.frontier.add_links(links)

      ## Store the fetched fetched_response
      self.storer.store(page_url, fetched_response)

      ## Update the limit
      self.limit -= 1

    self.logger.end_log()