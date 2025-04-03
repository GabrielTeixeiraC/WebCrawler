from bs4 import BeautifulSoup

"""
Parser class to parse HTML content using BeautifulSoup.
"""

class Parser:
  def __init__(self):
    """
    Initializes the Parser class.
    """
    pass

  def parse(self, html_content: str) -> list[str]:
    """
    Parses HTML content and extracts all links.
    Args:
        html_content (str): HTML content to be parsed.
    Returns:
        list[str]: List of extracted links.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    links = soup.find_all('a')
    return [link.get('href') for link in links if link.get('href') is not None]