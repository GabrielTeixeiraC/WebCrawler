from bs4 import BeautifulSoup

"""
Parser class to parse HTML content using BeautifulSoup.
"""
class Parser:
  def __init__(self, number_of_extracted_words: int = 20):
    """
    Initializes the Parser class.
    Args:
      number_of_extracted_words (int): Number of human-readable words to extract from the page.
    """
    self.number_of_extracted_words = number_of_extracted_words

  def parse(self, html_content: str) -> tuple[str, list[str], str, str]:
    """
    Parses HTML content and extracts all links.
    Args:
      html_content (str): HTML content to be parsed.
    Returns:
      html_content (str): Parsed HTML content.
      urls (list[str]): List of extracted links.
      title (str): Title of the page.
      first_visible_words (str): N first human-readable words from the page. N == 20 by default.
    """
    soup = BeautifulSoup(markup=html_content, features='html.parser')

    for tags_to_decompose in soup(['script', 'style', 'template']):
      tags_to_decompose.decompose()

    html_content = soup.prettify()
    
    # Extract all URLs that will be added to the frontier.
    urls = soup.find_all('a')

    # Extract the title and the first N human-readable words for logging.
    title = "No title found"
    title_tag = soup.title
    if title_tag and title_tag.string:
      title = title_tag.string.strip()

    self.title = title
    first_visible_words = self.extract_first_visible_words(soup_object=soup)

    return html_content, [url.get('href') for url in urls if url.get('href') is not None], title, first_visible_words
 
  def extract_first_visible_words(self, soup_object: BeautifulSoup) -> str:
    """
    Extracts the first N human-readable words from the parsed HTML content.
    Args:
      soup_object (BeautifulSoup): BeautifulSoup object containing the parsed HTML content.
    Returns:
      str: First N human-readable words from the page.
    """
    text = soup_object.get_text()
    
    # Split into words and take the first N
    words = text.split()
    return ' '.join(words[:self.number_of_extracted_words]) if words else ''