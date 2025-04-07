import json
import threading

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
    self.lock = threading.Lock()
    self.chunk = []
    self.first_entry_written = False

    if self.debug:
      # Start the file with an opening bracket
      with open(file=self.log_file, mode="w", encoding="utf-8") as f:
        f.write("[")

  def log(self, url: str, title: str, text: str, timestamp: int):
    """
    Logs the fetched HTML page.
    Args:
      url (str): URL of the fetched page.
      title (str): Title of the fetched page.
      text (str): Text from the fetched page.
      timestamp (int): Timestamp for when the page was fetched.
    """
    if not self.debug:
      return

    log_entry = {
      "URL": url,
      "Title": title,
      "Text": text,
      "Timestamp": timestamp
    }
    
    with self.lock:
      self.chunk.append(log_entry)
      if len(self.chunk) >= self.max_chunk_size:
        self.write_logs()

  def write_logs(self):
    """
    Writes the logs to the log file.
    This method writes the collected logs to the log file in JSON format.
    """
    if not self.chunk:
        return

    with open(self.log_file, "a", encoding="utf-8") as f:
      if self.first_entry_written:
        f.write(",\n")
      else:
        self.first_entry_written = True

      entries = [json.dumps(obj=entry, ensure_ascii=False, indent=2) for entry in self.chunk]
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
