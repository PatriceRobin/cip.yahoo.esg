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

# get Dow Jones Industrial companies
djurl = ('https://finance.yahoo.com/quote/%5EDJI/components?p=%5EDJI')
djpage = requests.get(djurl, headers).text
djsoup = bs(djpage, "lxml")
table1 = djsoup.find_all('table')
df1 = pd.read_html(str(table1))[0]
df_dj = pd.DataFrame(df1)


# adjust the dataframe / clean up
df_dj = df_dj.iloc[:, [0, 1]] #only keep symbol and company name
df_dj.rename(columns={'Symbol': 'symbol',
                      'Company Name': 'company'}, inplace=True) #rename columns
df_dj["company"] = df_dj["company"].str.replace(",", "") #replace commas with spaces for csv
df_dj = df_dj[df_dj.company != 'Dow Inc.'] #remove dow jones

# create an empty pd dataframe
df_yh = pd.DataFrame()

# get the financial data from the previous 5 years / monthly
for symbol, company in zip(df_dj.symbol, df_dj.company):
    # stock data
    url = ('https://finance.yahoo.com/quote/{}/history?period1=1447027200&period2=1604880000&interval=1mo&filter=history&frequency=1mo&includeAdjustedClose=true'.format(symbol))
    page = requests.get(url, headers).text
    soup = bs(page, "lxml")
    table2 = soup.find('table', {'class': "W(100%) M(0)"}) #find the right table
    df2 = pd.read_html(str(table2))[0] #extract table
    df_hist = pd.DataFrame(df2) #as panda df

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


#export as csv
df_yh.to_csv('yahoo.dow.jones.full.20201109.csv',
             encoding='utf-8', index=False)