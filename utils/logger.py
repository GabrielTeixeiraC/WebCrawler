import requests
import json

"""
Logger class for logging the fetched pages.
"""
class Logger:
  """
  Initializes the Logger class.
  Args:
    log_file (str): Path for the log file.
    max_chunk_size (int): Maximum number of in-memory cached entries.
  """
  def __init__(self, debug: bool = False, log_file: str = "log.json", max_chunk_size: int = 2):
    self.debug = debug
    self.log_file = log_file
    self.max_chunk_size = max_chunk_size
    self.chunk = []
    self.first_entry_written = False

    if self.debug:
      # Start the file with an opening bracket
      with open(self.log_file, "w", encoding="utf-8") as f:
        f.write("[")

  def log(self, fetched_response: requests.Response, timestamp: int):
    """
    Logs the fetched HTML page.
    Args:
      fetched_response (requests.Response): Fetched HTML page.
      timestamp (int): Timestamp for when the page was fetched.
    """
    if not self.debug:
      return

    url = fetched_response.url
    try:
      title = fetched_response.text.split("<title>")[1].split("</title>")[0]
    except IndexError:
      title = "No title found"
    text = fetched_response.text[:200]

    log_entry = {
      "url": url,
      "title": title,
      "text": text,
      "timestamp": timestamp
    }
    
    self.chunk.append(log_entry)

    if len(self.chunk) >= self.max_chunk_size:
      self.write_logs()

  def write_logs(self):
    """
    Writes the logs to the log file.
    This method writes the collected logs to the log file in JSON format.
    """
    if not self.debug or not self.chunk:
        return

    with open(self.log_file, "a", encoding="utf-8") as f:
      if self.first_entry_written:
        f.write(",\n")
      else:
        self.first_entry_written = True

      entries = [json.dumps(entry, ensure_ascii=False, indent=2) for entry in self.chunk]
      f.write(",\n".join(entries))
    
    self.chunk = []

  def end_log(self):
    """
    Ends the log file.
    This method closes the log file and adds a closing bracket.
    """
    if not self.debug:
      return
    
    self.write_logs()

    with open(self.log_file, "a", encoding="utf-8") as f:
      f.write("]\n")
