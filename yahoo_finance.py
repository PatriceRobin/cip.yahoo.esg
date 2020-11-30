#import packages
import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import re

# define user-agent
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Pragma': 'no-cache',
    'Referrer': 'https://google.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}

def get_soup(url):
    page = requests.get(url, headers).text
    return bs(page, "lxml")

def get_stock_index(url):
    tables = get_soup(url=url).find_all('table')
    table = pd.read_html(str(tables))[0]
    frame = pd.DataFrame(table)

    # adjust the dataframe / clean up
    frame = frame.iloc[:, [0, 1]] #only keep symbol and company name
    frame.rename(columns={'Symbol': 'symbol',
                        'Company Name': 'company'}, inplace=True) #rename columns
    frame["company"] = frame["company"].str.replace(",", "") #replace commas with spaces for csv
    frame = frame[frame.company != 'Dow Inc.'] #remove dow jones

    return frame

def get_stock_data(stock_index):
    # create an empty pd dataframe
    df_yh = pd.DataFrame()

    # get the financial data from the previous 5 years / monthly
    for symbol, company in zip(stock_index.symbol, stock_index.company):
        # stock data
        url = ('https://finance.yahoo.com/quote/{}/history?period1=1447027200&period2'\
            '=1604880000&interval=1mo&filter=history&frequency=1mo&includeAdjustedClose=true'.format(symbol))
        tables = get_soup(url=url).find('table', {'class': "W(100%) M(0)"}) #find the right table
        table = pd.read_html(str(tables))[0] #extract table
        df_hist = pd.DataFrame(table) #as panda df

        #clean up stock table
        df_hist = df_hist.iloc[:-1, [0, 5]] #remove the last row (description) and non-necessary columns
        df_hist.rename(columns={'Date': 'date', 'Adj Close**': 'stock'}, inplace=True) #rename columns
        df_hist = df_hist[pd.to_numeric(df_hist['stock'], errors='coerce').notnull()] #remove non-numeric values (splits & dividends)
        
        #add company name and symbol
        df_hist['company'] = company
        df_hist['symbol'] = symbol

        #sustainability score
        url_sub = ('https://finance.yahoo.com/quote/{}/sustainability?p={}'.format(symbol, symbol)) #access the sustainability page of every company in the dow jones industrial index
        page_sub = requests.get(url_sub, headers).text
        soup = bs(page_sub, "lxml")

        #environment
        df_hist['environment'] = soup.find('div', attrs={"data-reactid": "35"}).text

        #social socre
        df_hist['social'] = soup.find('div', attrs={"data-reactid": "43"}).text

        #governance score
        df_hist['governance'] = soup.find('div', attrs={"data-reactid": "50"}).text

        #overall substainability score
        df_hist['riskscore'] = soup.find('div', attrs={"class":"Fz(36px) Fw(600) D(ib) Mend(5px)"}).text
        
        # concat to empty pandas df
        df_yh = pd.concat([df_yh, df_hist], ignore_index=True, sort=True)

        return df_yh

def write_to_csv(df_yh):
    df_yh.to_csv('yahoo.dow.jones.full.20201109.csv',
                encoding='utf-8', index=False)