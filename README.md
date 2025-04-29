# Modular and Multithreaded Web Crawler
A high-performance, modular web crawler designed for efficient corpus collection. It uses multithreading to maximize throughput, respects robots.txt policies, and stores data in WARC format for later analysis. Built for research and large-scale web data collection tasks.

## 📌 Features
  
  - 🚀 Multithreaded architecture (configurable number of threads)

  - 🕸️ Robots.txt compliance using Protego

  - 🌐 Link extraction and deduplication

  - 🧠 HTML parsing with BeautifulSoup

  - 💾 Storage in WARC format via warcio

  - 🪵 JSONL logging for reproducibility and analysis

## 📂 Project Structure
```graphql
.
├── crawler/
│   ├── crawler.py       # Main Crawler class with multithreading
│   ├── frontier.py      # Manages the URL queue and deduplication
│   ├── fetcher.py       # Responsible for polite fetching and robots.txt
│   ├── parser.py        # Extracts links and content from pages
│   ├── storer.py        # Stores pages into WARC files
│   └── logger.py        # Async logging system
├── utils/
│   └── arg_parser.py    # Command-line argument parser
├── seeds.txt            # List of seed URLs
├── main.py              # Entry point for the crawler
└── README.md
```
## ⚙️ Installation
### 1. Clone the repository:
```bash
$ git clone https://https://github.com/GabrielTeixeiraC/WebCrawler.git
$ cd WebCrawler
```
### 2. Install dependencies:
```bash
$ python3 -m venv pa1
$ source pa1/bin/activate
$ pip3 install -r /path/to/requirements.txt
```

## 🚀 Usage
```bash
python main.py --seeds path/to/seeds.txt --limit 10000 --debug
```
## Arguments
| Argument     | Description                             |
|--------------|-----------------------------------------|
| `--seeds`    | Path to the file containing seed URLs   |
| `--limit`    | Maximum number of pages to crawl        |
| `--debug`    | Enable verbose logging (optional)       |