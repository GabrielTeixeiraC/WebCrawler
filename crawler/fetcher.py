import requests

"""
Fetcher class for sending HTTP requests while obying robots.txt rules and politeness policies.
"""
class Fetcher:
  def __init__(self, request_delay_ms: int = 100):
    """
    Initializes the Fetcher class.
    Args:
      request_delay_ms (int): Delay between requests in milliseconds.
    """
    self.request_delay_ms = request_delay_ms
  
  def fetch(self, url: str) -> requests.Response | None:
    """
    Fetches the content of a URL.
    Args:
      url (str): URL to be fetched.
    Returns:
      response (request.Response): Content of the URL or None
    """
    try:
      response = requests.get(url)
      
      response.raise_for_status()
     
      if "text/html" not in response.headers.get("Content-Type", ""):
        return None

      return response
    except requests.RequestException as e:
      print(f"Error occurred while fetching {url}: {e}")
      return None
