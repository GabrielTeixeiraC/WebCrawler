import queue
from url_normalize import url_normalize
from urllib3.util import parse_url

"""
Frontier class for managing the frontier of URLs to be crawled and implementing revisitation policies.
"""
class Frontier:
  def __init__(self, seeds: list[str], max_depth: int | None = None, timeout: float = 3.0):
    """
    Initializes the Frontier class.
    Args:
      seeds (list[str]): List of seed URLs.
      max_depth (int | None): Maximum depth for crawling. If None, no limit is set.
      timeout (float): Timeout for getting URLs from the queue.
    """
    self.max_depth = max_depth
    self.timeout = timeout
    self._queue = queue.Queue()
    self.visited = set() 
    for seed in seeds:
      self.add_url(seed, depth=0)

  def get_next_url(self) -> tuple[str, int] | tuple[None, None]:
    """
    Gets the next URL from the frontier.
    Returns:
      str: Next URL to be crawled.
      depth: Depth of the URL to be crawled.
    """
    try:
      next_url, depth = self._queue.get(timeout=self.timeout)
      return next_url, depth
    except queue.Empty:
      return None, None
    
  def has_urls(self) -> bool:
    """
    Checks if there are more URLs to crawl.
    Returns:
      bool: True if there are URLs left, False otherwise.
    """
    return not self._queue.empty()
  
  def add_url(self, url: str, depth: int):
    """
    Adds a new URL to the frontier.
    Args:
      url (str): New URL to be added.
    """
    if self.max_depth is not None and depth + 1 > self.max_depth:
      return

    try:
      parsed_url = parse_url(url)
      
      if not parsed_url.scheme or not parsed_url.host:
        return
      
      if parsed_url.scheme not in ["http", "https"]:
        return    
    except Exception as e:
      print(f"Failed to parse URL {url}: {e}")
      return    

    normalized_url = url_normalize(url=str(parsed_url), filter_params=True)

    if normalized_url not in self.visited:
      self.visited.add(normalized_url)
      self._queue.put((normalized_url, depth + 1))

  
  def add_urls(self, urls: list[str], current_depth: int = 0):
    """
    Adds multiple URLs to the frontier.
    Args:
      urls (list[str]): List of new URLs to be added.
    """
    for url in urls:
      self.add_url(url, depth=current_depth + 1)