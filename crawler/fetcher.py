import time
import requests

from urllib3.util import parse_url
from protego import Protego

"""
Fetcher class for sending HTTP requests while obeying robots.txt rules and politeness policies.
"""
class Fetcher:
  def __init__(self, default_crawl_delay_ms: int = 100, user_agent: str = "Web Crawler"):
    """
    Initializes the Fetcher class.
    Args:
      default_crawl_delay_ms (int): Default delay between requests in milliseconds.
      user_agent (str): User agent string to be used in the requests.
    """
    self.default_crawl_delay_ms = default_crawl_delay_ms

    # Maps domain names to their robots.txt parsers.
    self.robots_parsers = {}

    # Create a session to reutilize TCP connections.
    self.session = requests.Session()
    self.session.headers.update({"User-Agent": user_agent})
  
  def get_domain(self, url: str) -> str | None:
    """
    Extracts the domain from a URL.
    Args:
      url (str): URL to extract the domain from.
    Returns:
      str: Domain name. Returns None if the URL is invalid.
    """
    parsed = parse_url(url)
    if not parsed.scheme or not parsed.host:
      return None
    return f"{parsed.scheme}://{parsed.host}"
  
  def get_robots_parser(self, url: str) -> Protego:
    """
    Returns the robots.txt parser for a given URL.
    Args:
      url (str): URL to get the robots.txt parser for.
    Returns:
      Protego: Robots.txt parser for the base URL.
    """
    domain = self.get_domain(url=url)
    if domain is None:
      return Protego()

    if domain not in self.robots_parsers:
      robots_url = f"{domain}/robots.txt"
      try:
        response = self.session.get(robots_url)
        response.raise_for_status()
        self.robots_parsers[domain] = Protego.parse(content=response.text)
      except requests.RequestException as e:
        self.robots_parsers[domain] = Protego()
    return self.robots_parsers[domain]


  def fetch(self, url: str) -> requests.Response | None:
    """
    Fetches the content of a URL.
    Args:
      url (str): URL to be fetched.
    Returns:
      response (request.Response): Content of the URL or None
      timestamp (int): Timestamp of when the URL was fetched.
    """
    robots_parser = self.get_robots_parser(url=url)
    user_agent = self.session.headers["User-Agent"] 
    
    if not robots_parser.can_fetch(url=url, user_agent=user_agent):
      return None 

    crawl_delay_seconds = robots_parser.crawl_delay(user_agent=user_agent)
    crawl_delay = crawl_delay_seconds if crawl_delay_seconds is not None else self.default_crawl_delay_ms / 1000
    time.sleep(crawl_delay) 

    try:
      timestamp = int(time.time())
      response = self.session.get(url)
      
      response.raise_for_status()
     
      if "text/html" not in response.headers.get("Content-Type", ""):
        return None

      return response, timestamp
    except requests.RequestException as e:
      print(f"Error occurred while fetching {url}: {e}")
      return None

  def close(self):
    """
    Closes the session and clears the robots parsers dictionary.
    """
    self.session.close()
    self.robots_parsers.clear()
