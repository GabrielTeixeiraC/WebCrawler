from utils import arg_parser
from crawler.crawler import Crawler

def main():
  """
  Main function.
  """
  seeds_path, limit, debug = arg_parser.parse_args()

  if (debug):
    print("Debug mode enabled.")
    print("Seeds path:", seeds_path)
    print("Limit:", limit)
  
  try:
    with open(seeds_path, "r") as f:
      seeds = f.readlines()
  except FileNotFoundError:
    print("Seeds file not found.")
    exit()

  seeds = [seed.strip() for seed in seeds]

  crawler = Crawler(seeds, limit, debug)
  crawler.crawl()

if __name__ == "__main__":
  main()