import os
import io
import threading
import requests
from warcio.warcwriter import WARCWriter
from warcio.statusandheaders import StatusAndHeaders

"""
Storer class for storing the fetched HTML pages.
"""
class Storer:
  def __init__(self, pages_per_file: int = 1000, corpus_folder_path: str = "./corpus/"):
    """
    Initializes the Storer class.
    Args:
      pages_per_file (int): Number of pages that will be stored in each WARC file.
      corpus_folder_path (str): Path for the folder where the WARC files will be stored
    """
    self.pages_per_file = pages_per_file
    self.corpus_folder_path = corpus_folder_path
    self.pages_in_current_file = 0
    self.current_file_index = 0

    self.output_file = None
    self.finished = False
    self.writer = None
    self.lock = threading.Lock()

    # Ensure that the output directory exists
    os.makedirs(self.corpus_folder_path, exist_ok=True)
    self.open_new_file()

  def open_new_file(self):
    """
    Opens a new WARC file for writing.
    """
    if self.output_file:
      self.output_file.close()

    # Create the path for the next WARC file
    warc_path = f"{self.corpus_folder_path}file_{self.current_file_index}.warc.gz"
    self.output_file = open(warc_path, 'wb')
    # Create a new WARC writer that compresses the output
    self.writer = WARCWriter(filebuf=self.output_file, gzip=True)

  def store(self, url: str, html_content: str, fetched_response: requests.Response):
    """
    Stores the fetched HTML page to a WARC file. Each WARC file has 1000 pages.
    Args:
      url (str): Fetched URL.
      html_content (str): Fetched page's HTML content.
      fetched_response (requests.Response): Fetched page's response object.
    """
    with self.lock:
      if self.finished:
        # Prevent writing if storage has been finalized
        return

      # Encode HTML content safely
      encoded_html_content = html_content.encode("utf-8", errors='replace')
      headers_list = fetched_response.raw.headers.items()

      # Create HTTP headers for the WARC record
      http_headers = StatusAndHeaders(statusline="200 OK", headers=headers_list, protocol="HTTP/1.0")

      # Create a WARC "response" record
      record = self.writer.create_warc_record(
        uri=url,
        record_type="response",
        payload=io.BytesIO(encoded_html_content),
        http_headers=http_headers
      )

      # Write the WARC record to the file
      self.writer.write_record(record)

      self.pages_in_current_file += 1

      # Rotate file if maximum pages per file reached
      if self.pages_in_current_file >= self.pages_per_file:
        self.pages_in_current_file = 0
        self.current_file_index += 1
        self.open_new_file()

  def finish(self):
    """
    Finishes the storer by closing the current WARC file and preventing further writes.
    This method should be called when the crawling process is finished.
    """
    with self.lock:
      self.finished = True
      if self.output_file:
        self.output_file.close()
