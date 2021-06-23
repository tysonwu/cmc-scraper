"""
This script scrapes market cap data of top N coins
for each day in a pre-specified date range and 1<=N<=199
"""
import time
import os
import re
import argparse
from datetime import datetime, timedelta

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def scrape_cmc(driver, date, top=None):
    """
    Scrape market cap data of top N coins at pre-specified date
    default top=None and return all results (max 199)
    """
    # the selenium way to get data
    driver.get(f'https://coinmarketcap.com/historical/{date}/')
    
    for x in range(0,8000,400): # slow scroll
        driver.execute_script(f'window.scrollTo(0,{x})')
        time.sleep(0.2)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'lxml')

    soup_rows = soup.findAll('tr', {'class':'cmc-table-row'})

    soup_list = []
    for row in soup_rows:
        soup_list.append([td.text for td in row.findAll('td') if td.text != ''])
    
    # convert into dataframe
    colnames = ['rank','coin','symbol','market_cap','price','supply','volume_24h','pct_1h','pct_24h','pct_7d']
    df = pd.DataFrame(soup_list, columns=colnames)
    # clean dataframe

    df['market_cap'] = df['market_cap'].apply(lambda x: x.split('$')[-1])

    for col in ['market_cap','price','volume_24h']:
        # pprint(df[col].to_list())
        # print(df[col].to_list())
        df[col] = df[col].apply(lambda x: re.sub(r'[\$,<>]','',x))
        df[col] = df[col].astype(float)
    
    for col in ['rank']:
        df[col] = df[col].astype(int)

    # remove non-digits
    for col in ['supply']:
        df[col] = df[col].apply(lambda x: re.sub(r'\D','',x)).astype(float)

    # convert percentages
    for col in ['pct_1h','pct_24h','pct_7d']:
        df[col] = df[col].apply(lambda x: re.sub(r'[\$,<>\%]','',x))
        df[col] = df[col].apply(lambda x: float(x.strip('%'))/100)
    
    if top:
        df = df[df['rank'] <= top]

    # output
    df.to_csv(f'data/cmc_snapshots/cmc_snapshot_{date}.csv', index=False)
    print(df.head())
    print(f'Saved snapshot to output - {date}')


if __name__ == '__main__':
    #------------CONFIG---------------#
    top = 150
    
    parser = argparse.ArgumentParser(description='startdate enddate (in YYYYMMDD)')
    parser.add_argument('-start')
    parser.add_argument('-end')
    args = parser.parse_args()
    start_date = args.start
    end_date = args.end

    #---------------------------------#

    start_dt = datetime.strptime(start_date, '%Y%m%d')
    end_dt = datetime.strptime(end_date, '%Y%m%d')
    delta = end_dt - start_dt

    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36")
    driver = webdriver.Chrome(executable_path=r'./driver/chromedriver', options=chrome_options)

    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)

    for dt in range(delta.days+1):
        snapshot = datetime.strftime(start_dt + timedelta(days=dt),'%Y%m%d')
        scrape_cmc(driver=driver, date=snapshot, top=top)

    driver.close()