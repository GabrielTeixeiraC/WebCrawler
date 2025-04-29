import time
import requests

from urllib3.util import parse_url
from urllib3.exceptions import LocationParseError
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

    # Create a persistent HTTP session (reuses TCP connections, faster crawling).
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
    try:
      parsed = parse_url(url)
      
      return f"{parsed.scheme}://{parsed.host}"
    except LocationParseError:
      print(f"Invalid URL: {url}")
      return None
  
  def get_robots_parser(self, url: str) -> Protego:
    """
    Returns the robots.txt parser for a given URL.
    Args:
      url (str): URL to get the robots.txt parser for.
    Returns:
      Protego: Robots.txt parser for the base URL.
    """
    domain = self.get_domain(url=url)

    # If domain can't be extracted, use an empty parser that allows everything.
    if domain is None:
      return Protego()

    if domain not in self.robots_parsers:
      robots_url = f"{domain}/robots.txt"
      try:
        response = self.session.get(robots_url)
        response.raise_for_status()

        # Parse robots.txt content and cache it
        self.robots_parsers[domain] = Protego.parse(content=response.text)
      except Exception as e:
        print(f"Error occurred while parsing robots.txt for {domain}: {e}")

        # On any error, assume no restrictions
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
    

    # Check if the URL can be fetched according to robots.txt
    if not robots_parser.can_fetch(url=url, user_agent=user_agent):
      return None, None 

    # Respect crawl delay (if specified), otherwise use default
    crawl_delay_seconds = robots_parser.crawl_delay(user_agent=user_agent)
    crawl_delay = crawl_delay_seconds if crawl_delay_seconds is not None else self.default_crawl_delay_ms / 1000
    time.sleep(crawl_delay) 

    try:
      timestamp = int(time.time())
      response = self.session.get(url, timeout=(10, 20)) # (connect timeout, read timeout)
      response.encoding = 'utf-8'  # Force UTF-8 encoding for consistency
 
      response.raise_for_status() # Raise exception if status code is 4xx or 5xx
     
      if "text/html" not in response.headers.get("Content-Type", ""):
        return None, None

      return response, timestamp
    except Exception as e:
      print(f"Error occurred while fetching {url}: {e}")
      return None, None

  def close(self):
    """
    Closes the session and clears the robots parsers dictionary.
    """
    self.session.close()
    self.robots_parsers.clear()
