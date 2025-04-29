import requests
import json
import threading
import time

"""
Logger class for logging the fetched pages.
"""
class Logger:
  """
  Initializes the Logger class.
  Args:
    log_file_path (str): Path for the log file.
    flush_interval (float): Interval in seconds for flushing logs.
  """
  def __init__(self, debug: bool = False, log_file_path: str = "tmp/log.jsonl", flush_interval: float = 3.0):
    self.debug = debug
    self.log_file_path=log_file_path 
    self.flush_interval = flush_interval
    self.chunk = []   # Temporary storage for log entries before writing to disk
    self.lock = threading.Lock()  # Lock to ensure thread-safe access to 'chunk'
    self.stop_event = threading.Event()   # Event to signal the logging thread to stop


    if self.debug:
      # Create/clear the log file initially
      with open(file=self.log_file_path, mode="w", encoding="utf-8") as f:
        pass

      # Start the background worker thread responsible for flushing logs
      self.worker_thread = threading.Thread(target=self._log_worker, name="LoggerThread", daemon=True)
      self.worker_thread.start()

  def log(self, url: str, title: str | None, text: str | None, timestamp: int):
    """
    Logs the fetched HTML page.
    Args:
      url (str): URL of the fetched page.
      title (str | None): Title of the fetched page. None if debug is disabled.
      text (str | None): Text from the fetched page. None if debug is disabled.
      timestamp (int): Timestamp for when the page was fetched.
    """
    if not self.debug:
      return

    # Structure of a single log entry
    log_entry = {
      "URL": url,
      "Title": title,
      "Text": text,
      "Timestamp": timestamp
    }

    # Add the log entry to the in-memory chunk in a thread-safe way
    with self.lock:
      self.chunk.append(log_entry)

  def _log_worker(self):
    """
    Worker thread that flushes logs to file every `flush_interval` seconds.
    """
    while not self.stop_event.is_set():
      time.sleep(self.flush_interval)
      self.write_logs()

    # Final flush before exiting the thread
    self.write_logs()

  def write_logs(self):
    """
    Writes the logs to the log file in JSONL format.
    """
    with self.lock:
      if not self.chunk:
        return

      with open(self.log_file_path, "a", encoding="utf-8") as f:
        for entry in self.chunk:
          json.dump(entry, f, ensure_ascii=False)
          f.write("\n")

      # Clear chunk after writing
      self.chunk = []

  def end_log(self):
    """
    Stops the logger and flushes any remaining logs.
    """
    if not self.debug:
      return

    self.stop_event.set()
    self.worker_thread.join()
