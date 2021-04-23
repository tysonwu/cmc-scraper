"""
This script scrapes market cap data of top N coins
for each day in a pre-specified date range and 1<=N<=199
"""

from datetime import datetime, timedelta
import time
from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
import argparse
import os


def scrape_cmc(date, top=None):
    """
    Scrape market cap data of top N coins at pre-specified date
    default top=None and return all results (max 199)
    """
    url = f'https://coinmarketcap.com/historical/{date}/'
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    r = requests.get(url=url, headers=header)
    time.sleep(7) # rest for awhile
    soup = BeautifulSoup(r.content, 'lxml')
    soup_rows = soup.findAll('tr', {'class':'cmc-table-row'})
    # colnames = [col.text for col in soup.findAll(
    #     'div', {'class':'cmc-table__table-wrapper-outer'}
    #     )[0].findAll('th') if col.text!='']
    # print(colnames)
    soup_list = []
    for row in soup_rows:
        soup_list.append([td.text for td in row.findAll('td') if td.text != ''])
    
    # convert into dataframe
    colnames = ['rank','coin','symbol','market_cap','price','supply','volume_24h','pct_1h','pct_24h','pct_7d']
    df = pd.DataFrame(soup_list, columns=colnames)
    # print(df)
    # clean dataframe
    for col in ['market_cap','price','volume_24h']:
        # print(col)
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
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)
    
    df.to_csv(f'{OUTPUT_PATH}/cmc_snapshot_{date}.csv', index=False)
    print(df.head())
    print(f'Saved snapshot to output - {date}')


if __name__ == '__main__':
    #------------CONFIG---------------#
    top = 150
    OUTPUT_PATH = f'./output'
    
    parser = argparse.ArgumentParser(description='startdate enddate (in YYYYMMDD)')
    parser.add_argument('-start')
    parser.add_argument('-end')
    args = parser.parse_args()
    start_date = args.start
    end_date = args.end

    # start_date = '20201217' # '20140601'
    # end_date = '20201229'
    #---------------------------------#

    start_dt = datetime.strptime(start_date, '%Y%m%d')
    end_dt = datetime.strptime(end_date, '%Y%m%d')
    delta = end_dt - start_dt

    for dt in range(delta.days+1):
        snapshot = datetime.strftime(start_dt + timedelta(days=dt),'%Y%m%d')
        scrape_cmc(date=snapshot, top=top)
