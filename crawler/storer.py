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
  def __init__(self, pages_per_file: int = 2, corpus_folder_path: str = "./corpus/"):
    self.pages_per_file = pages_per_file
    self.pages_in_current_file = 0
    self.current_file_index = 0
    self.corpus_folder_path = corpus_folder_path

  def store(self, url: str,  fetched_response: requests.Response):
    """
    Stores the fetched HTML page to a WARC file. Each WARC file has 1000 pages.
    Args:
      url (str): Fetched URL.
      fetched_response (requests.Response): Fetched HTML page.
    """
    with open(file=f"{self.corpus_folder_path}file_{self.current_file_index}.warc.gz", mode='ab') as output:
      writer = WARCWriter(filebuf=output, gzip=True)

      html_content = fetched_response.text.encode("utf-8")  # Encode HTML as bytes
      headers_list = fetched_response.raw.headers.items()

      http_headers = StatusAndHeaders(statusline='200 OK', headers=headers_list, protocol='HTTP/1.0')

      record = writer.create_warc_record(uri=url, record_type="application/http; msgtype=response",
                                          # payload=io.BytesIO(html_content), Commenting this just to make debugging easier
                                          http_headers=http_headers)

      writer.write_record(record)

    self.pages_in_current_file += 1
    if self.pages_in_current_file >= self.pages_per_file:
      self.pages_in_current_file = 0
      self.current_file_index += 1
      
