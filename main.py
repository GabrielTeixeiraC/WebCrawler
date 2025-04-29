from utils import arg_parser
from crawler.crawler import Crawler

def main():
  """
  Main function.
  """
  # Parse command-line arguments
  seeds_path, limit, debug = arg_parser.parse_args()

  if (debug):
    print("Debug mode enabled.")
    print("Seeds path:", seeds_path)
    print("Limit:", limit)
  
  try:
    # Read the seed URLs from the specified file
    with open(seeds_path, "r") as f:
      seeds = f.readlines()
  except FileNotFoundError:
    print("Seeds file not found.")
    exit()

  # Clean up each seed (remove whitespace and newlines)
  seeds = [seed.strip() for seed in seeds]

  # Define the number of threads for the crawler
  thread_count = 100

  # Initialize the crawler with the parsed arguments
  crawler = Crawler(seeds=seeds, limit=limit, debug=debug, thread_count=thread_count)

  # Start the crawling process
  crawler.crawl()

# Entry point for script execution
if __name__ == "__main__":
  main()