import queue
"""
Frontier class for managing the frontier of URLs to be crawled and implementing revisitation policies.
"""

class Frontier:
  def __init__(self, seeds: list[str], debug: bool):
    """
    Initializes the Frontier class.
    Args:
        seeds (list[str]): List of seed URLs.
        debug (bool): Enable debug mode.
    """
    self.debug = debug
    self._queue = queue.Queue()
    for seed in seeds:
      self._queue.put(seed)

  def get_next_url(self) -> str:
    """
    Gets the next URL from the frontier.
    Returns:
        str: Next URL to be crawled.
    """
    if not self._queue.empty():
      return self._queue.get()
    else:
      return None
    
  def has_urls(self) -> bool:
    """
    Checks if there are more URLs to crawl.
    Returns:
        bool: True if there are URLs left, False otherwise.
    """
    return not self._queue.empty()
  
  def add_links(self, links: list[str]):
    """
    Adds new links to the frontier.
    Args:
        links (list[str]): List of new links to be added.
    """
    for link in links:
      self._queue.put(link)