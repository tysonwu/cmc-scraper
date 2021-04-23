# cmc-scraper

- A simple web scraper to obtain historical cryptocurrency market data from coinmarketcap.com
- Run the script by the following shell command `python cmc_scraper -start YYYYMMDD -end YYYYMMDD` to get data between a range in csv format

- The scraper defaults to scrape data for daily top 150 ranked coins. This number can be adjusted in the `CONFIG` session inside the script