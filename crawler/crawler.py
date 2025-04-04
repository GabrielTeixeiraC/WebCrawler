from .fetcher import Fetcher
from .parser import Parser
from .storer import Storer
from .frontier import Frontier

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
        limit (int): Number of seeds to be used.
        debug (bool): Enable debug mode.
    """
    self.seeds = seeds
    self.limit = limit
    self.debug = debug
    self.frontier = Frontier(seeds[:limit], debug)
    self.fetcher = Fetcher()
    self.parser = Parser()
    self.storer = Storer() 

  def crawl(self):
    """
    Starts the crawling process.
    This method fetches URLs from the frontier, parses the content,
    and stores the results. It continues until the limit is reached or
    there are no more URLs to crawl.
    """
    while self.frontier.has_urls() and self.limit > 0:
      ## Get the next URL
      next_url = self.frontier.get_next_url()
      
      ## Fetch the URL
      fetched_response = self.fetcher.fetch(next_url)

      if fetched_response is None:
        print(f"Failed to fetch {next_url}.")
        continue

      ## Parse the content
      links = self.parser.parse(fetched_response.text)
      self.frontier.add_links(links)

      ## Store the fetched fetched_response
      self.storer.store(next_url, fetched_response)

      ## Update the limit
      self.limit -= 1