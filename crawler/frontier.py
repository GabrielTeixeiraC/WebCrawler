import queue
import threading

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
    self._queue = queue.Queue() # Queue to manage the frontier
    self.visited = set() # Set to track visited URLs (avoid duplicates)
    for seed in seeds:
      self.add_url(seed, depth=0)

  def get_next_url(self, stop_signal: threading.Event | None = None) -> tuple[str, int] | tuple[None, None]:
    """
    Gets the next URL from the frontier.
    Returns:
      str: Next URL to be crawled.
      depth: Depth of the URL to be crawled.
    """
    try:
      # If a stop signal is provided and triggered, return None immediately
      if stop_signal is not None and stop_signal.is_set():
        return None, None

      # Try to get the next URL and its depth
      next_url, depth = self._queue.get(timeout=self.timeout)
      return next_url, depth
    except queue.Empty:
      # If no URL is available within the timeout, return None
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
    # Check depth constraint
    if self.max_depth is not None and depth + 1 > self.max_depth:
      return

    try:
      # Validate that the URL has a proper scheme and host
      parsed_url = parse_url(url)
      
      if not parsed_url.scheme or not parsed_url.host:
        return

      # Accept only HTTP or HTTPS URLs
      if parsed_url.scheme not in ["http", "https"]:
        return    
    except Exception as e:
      print(f"Failed to parse URL {url}: {e}")
      return    

    try:
      # Normalize the URL (remove redundant parameters, unify formatting)
      normalized_url = url_normalize(url=str(parsed_url), filter_params=True)
    except Exception as e:
        print(f"Failed to normalize URL {url}: {e}")
        return

    # Only add the URL if it has not been visited before
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