import queue
from url_normalize import url_normalize

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
    self.visited = set()
    self.add_links(seeds)

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
  
  def add_link(self, link: str):
    """
    Adds a new link to the frontier. A revisitation policy is implemented to avoid adding duplicate links.
    Args:
      link (str): New link to be added.
    """
    normalized_link = url_normalize(link, filter_params=True)
    if normalized_link not in self.visited:
      self.visited.add(normalized_link)
      self._queue.put(normalized_link)
  
  def add_links(self, links: list[str]):
    """
    Adds multiple links to the frontier.
    Args:
      links (list[str]): List of new links to be added.
    """
    for link in links:
      self.add_link(link)
