import argparse

def parse_args():
  """
  Parses command-line arguments.
  Returns:
      tuple: (seeds_path, limit, debug)
  """
  # Initialize the argument parser
  parser = argparse.ArgumentParser(description="Web Crawler Argument Parser")

  parser.add_argument("-s", "--seeds", type=str, required=True, help="Path to the seeds file")
  parser.add_argument("-n", "--limit", type=int, required=True, help="Limit for the number of pages to crawl")
  parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")

  # Parse the command-line arguments
  args = parser.parse_args()

  # Validate that the seeds file is a .txt file
  if not args.seeds.endswith(".txt"):
      parser.error("Seeds file must be a .txt file.")

  # Validate that limit is non-negative
  if args.limit < 0:
      parser.error("Limit must be a non-negative integer.")

  return args.seeds, args.limit, args.debug
