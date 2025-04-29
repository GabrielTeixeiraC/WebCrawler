from bs4 import BeautifulSoup

"""
Parser class to parse HTML content using BeautifulSoup.
"""
class Parser:
  def __init__(self, number_of_extracted_words: int = 20, debug: bool = False):
    """
    Initializes the Parser class.
    Args:
      number_of_extracted_words (int): Number of human-readable words to extract from the page.
      debug (bool): Enable debug mode.
    """
    self.number_of_extracted_words = number_of_extracted_words
    self.debug = debug
    self.max_length = 500 # Maximum length for title and first visible words

  def parse(self, html_content: str) -> tuple[str, list[str], str | None, str | None]:
    """
    Parses HTML content and extracts all links.
    Args:
      html_content (str): HTML content to be parsed.
    Returns:
      html_content (str): Parsed HTML content.
      urls (list[str]): List of extracted links.
      title (str | None): Title of the page. None if debug is disabled.
      first_visible_words (str | None): N first human-readable words from the page. N == 20 by default. None if debug is disabled.
    """
    # Create BeautifulSoup object
    soup = BeautifulSoup(markup=html_content, features='html.parser')

    # Remove non-visible content: scripts, styles, templates
    for tags_to_decompose in soup(['script', 'style', 'template']):
      tags_to_decompose.decompose()

    # Prettify the HTML (format it nicely)
    html_content = soup.prettify()
    
    # Extract all URLs that will be added to the frontier.
    urls = soup.find_all('a')
    urls = [url.get('href') for url in urls if url.get('href') is not None]

    if not self.debug:
      # If not in debug mode, return only HTML and URLs
      return html_content, urls, None, None

    # If in debug mode, also extract and truncate the title
    title = self.extract_title(soup_object=soup)
    truncated_title = title[:self.max_length] if len(title) > self.max_length else title

    # Extract and truncate the first N human-readable words
    first_visible_words = self.extract_first_visible_words(soup_object=soup)
    truncated_first_visible_words = first_visible_words[:self.max_length] if len(first_visible_words) > self.max_length else first_visible_words

    return html_content, urls, truncated_title, truncated_first_visible_words

  def extract_title(self, soup_object: BeautifulSoup) -> str:
    """
    Extract the title from the page for logging. 
    Args:
      soup_object (BeautifulSoup): BeautifulSoup object containing the parsed HTML content.
    Returns:
      str: Title of the page.
    """
    title = "No title found"
    title_tag = soup_object.title

    if title_tag and title_tag.string:
      title = title_tag.string.strip()
    
    return title
  
  def extract_first_visible_words(self, soup_object: BeautifulSoup) -> str:
    """
    Extracts the first N human-readable words from the parsed HTML content.
    Args:
      soup_object (BeautifulSoup): BeautifulSoup object containing the parsed HTML content.
    Returns:
      str: First N human-readable words from the page.
    """
    # Get all visible text from the page
    text = soup_object.get_text()
    
    # Split into words and take the first N
    words = text.split()
    return ' '.join(words[:self.number_of_extracted_words]) if words else ''