#import packages
import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import re

#define agent
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Pragma': 'no-cache',
    'Referrer': 'https://google.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}

#get dow jones companies
djurl = ('https://finance.yahoo.com/quote/%5EDJI/components?p=%5EDJI')
djpage = requests.get(djurl,headers).text
djsoup = bs(djpage, "lxml")
table1 = djsoup.find_all('table')
df1 = pd.read_html(str(table1))[0]
df_dj=pd.DataFrame(df1)


#adjust the dataframe
df_dj = df_dj.iloc[:,[0,1]]
df_dj.rename(columns = {'Symbol':'symbol', 'Company Name':'company'}, inplace = True)
df_dj = df_dj.head(2)


df_yh  = pd.DataFrame()
#,'company','riskscore','environment','social','governance'

#get the financial data from the previous 5 years / monthly
#for 
for symbol, company in zip(df_dj.symbol, df_dj.company):
    #load the table
    url = ('https://finance.yahoo.com/quote/{}/history?period1=1447027200&period2=1604880000&interval=1mo&filter=history&frequency=1mo&includeAdjustedClose=true'
    .format(symbol))
    page = requests.get(url,headers).text
    soup = bs(page, "lxml")
    table2 = soup.find('table',{'class':"W(100%) M(0)"})
    df2=pd.read_html(str(table2))[0]

    #clean df_hist table
    df_hist=pd.DataFrame(df2)
    df_hist = df_hist.iloc[:-1,[0,5]]
    df_hist.rename(columns = {'Date':'date', 'Adj Close**':'stock'}, inplace = True)
    df_hist = df_hist[~df_hist.stock.str.contains('Dividend')]
    
    #take the symbols and company from df_dj
    df_hist['company'] = company
    df_hist['symbol'] = symbol
    
#get ESG score (2020.11.09)
    #load page
    url2 = ('https://finance.yahoo.com/quote/{}/sustainability?p={}'
    .format(symbol,symbol))
    page2 = requests.get(url2,headers).text
    soup2 = bs(page2, "lxml")

    #scrap the ESG scores
    df_hist['riskscore']= soup2.find('div', attrs={"class":"Fz(36px) Fw(600) D(ib) Mend(5px)"}).text
    df_hist['environment'] = soup2.find('div', attrs={"data-reactid": "35"}).text
    df_hist['social'] = soup2.find('div', attrs={"data-reactid": "43"}).text
    df_hist['governance'] = soup2.find('div', attrs={"data-reactid": "50"}).text

    #concat
    df_yh = pd.concat([df_yh,df_hist], ignore_index=True, sort=True)


df_yh.to_csv('yahoo.dow.jones.test.csv',
              encoding='utf-8', index=False)
