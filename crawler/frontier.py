import queue
from url_normalize import url_normalize

"""
Frontier class for managing the frontier of URLs to be crawled and implementing revisitation policies.
"""
class Frontier:
  def __init__(self, seeds: list[str], max_depth: int | None = None):
    """
    Initializes the Frontier class.
    Args:
        seeds (list[str]): List of seed URLs.
    """
    self.max_depth = max_depth
    self._queue = queue.Queue()
    self.visited = set() 
    for seed in seeds:
      normalized = url_normalize(url=seed, filter_params=True)
      if normalized not in self.visited:
        self.visited.add(normalized)
        self._queue.put((normalized, 0))

  def get_next_url(self) -> tuple[str, int] | tuple[None, None]:
    """
    Gets the next URL from the frontier.
    Returns:
        str: Next URL to be crawled.
        depth: Depth of the URL to be crawled.
    """
    if not self._queue.empty():
      next_url, depth = self._queue.get()
      return next_url, depth 
    return None, None
    
  def has_urls(self) -> bool:
    """
    Checks if there are more URLs to crawl.
    Returns:
        bool: True if there are URLs left, False otherwise.
    """
    return not self._queue.empty()
  
  def add_links(self, links: list[str], current_depth: int = 0):
    """
    Adds multiple links to the frontier.
    Args:
      links (list[str]): List of new links to be added.
    """
    if self.max_depth is not None and current_depth + 1 > self.max_depth:
      return
    
    for link in links:
      normalized_link = url_normalize(url=link, filter_params=True)
      if normalized_link not in self.visited:
        self.visited.add(normalized_link)
        self._queue.put((normalized_link, current_depth + 1))
