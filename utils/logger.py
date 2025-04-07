import json
import queue
import threading

"""
Logger class for logging the fetched pages.
"""
class Logger:
  """
  Initializes the Logger class.
  Args:
    debug (bool): Enable debug mode.
    log_file (str): Path for the log file.
    flush_interval (float): Interval for flushing the log entries to the file.
  """
  def __init__(self, debug: bool = False, log_file: str = "log.json", flush_interval: float = 1.0):
    self.debug = debug
    self.log_file = log_file
    self.flush_interval = flush_interval
    self.stop_event = threading.Event()
    self.queue = queue.Queue()
    self.lock = threading.Lock()
    self.first_entry_written = False

    if self.debug:
      # Start the file with an opening bracket
      with open(file=self.log_file, mode="w", encoding="utf-8") as f:
        f.write("[")

      self.worker_thread = threading.Thread(target=self._log_worker, name="LoggerThread", daemon=True)
      self.worker_thread.start()

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
    
    self.queue.put(log_entry)

  def _log_worker(self):
    """
    Worker thread for logging.
    This method continuously checks the queue for new log entries and writes them to the log file.
    """
    buffer = []

    while not self.stop_event.is_set() or not self.queue.empty():
        try:
            log_entry = self.queue.get(timeout=self.flush_interval)
            buffer.append(log_entry)
        except queue.Empty:
            pass

        if buffer:
            self._flush(entries=buffer)
            buffer.clear()

  def _flush(self, entries):
    """
    Writes the logs to the log file.
    This method writes the collected logs to the log file in JSON format.
    """
    with self.lock:
      with open(self.log_file, "a", encoding="utf-8") as f:
        if self.first_entry_written:
          f.write(",\n")
        else:
          self.first_entry_written = True

        json_entries = [json.dumps(entry, ensure_ascii=False, indent=2) for entry in entries]
        f.write(",\n".join(json_entries))

  def end_log(self):
    """
    Ends the log file.
    This method closes the log file and adds a closing bracket.
    """
    if not self.debug:
        return

    self.stop_event.set()
    self.worker_thread.join()

    with open(self.log_file, "a", encoding="utf-8") as f:
        f.write("]\n")