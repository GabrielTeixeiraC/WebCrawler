import io
import requests
from warcio.warcwriter import WARCWriter
from warcio.statusandheaders import StatusAndHeaders

"""
Storer class for storing the fetched HTML pages.
"""
class Storer:
  """
  Initializes the Storer class.
  Args:
    pages_per_file (int): Number of pages that will be stored in each WARC file.
    corpus_folder_path (str): Path for the folder where the WARC files will be stored
  """
  def __init__(self, pages_per_file: int = 100, corpus_folder_path: str = "./corpus/"):
    self.pages_per_file = pages_per_file
    self.pages_in_current_file = 0
    self.current_file_index = 0
    self.corpus_folder_path = corpus_folder_path

  def store(self, url: str, html_content: str, fetched_response: requests.Response):
    """
    Stores the fetched HTML page to a WARC file. Each WARC file has 1000 pages.
    Args:
      url (str): Fetched URL.
      html_content (str): Fetched page's HTML content.
      fetched_response (requests.Response): Fetched page's response object.
    """
    with open(file=f"{self.corpus_folder_path}file_{self.current_file_index}.warc.gz", mode='ab') as output:
      writer = WARCWriter(filebuf=output, gzip=True)

      encoded_html_content = html_content.encode("utf-8", errors='replace')
      headers_list = fetched_response.raw.headers.items()

      http_headers = StatusAndHeaders(statusline='200 OK', headers=headers_list, protocol='HTTP/1.0')

      record = writer.create_warc_record(uri=url, record_type="application/http; msgtype=response",
                                          payload=io.BytesIO(encoded_html_content),
                                          http_headers=http_headers)

      writer.write_record(record)

    self.pages_in_current_file += 1
    if self.pages_in_current_file >= self.pages_per_file:
      self.pages_in_current_file = 0
      self.current_file_index += 1
      
