#import packages for yahoo
import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import re

#import packages for esg
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import time
import os.path
import csv

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
        df_hist['date'] = pd.to_datetime(df_hist['date']).dt.to_period('M')
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


def get_esg_from_html(stock_index):
    # result array with all esg ratigns
    all_ratings = []

    for symbol in stock_index.symbol:
        # result array with esg ratigns for current ticker
        ratings = []

        # open saved html file
        filename = "./esg.html/" + symbol + ".html"
        if(os.path.isfile(filename) == False):
            print("Error: File for ticker: " + symbol + " not found.")
            continue
        else:
            f = open(filename, "r",  encoding='utf-8')
            html_content = f.read()
            soup = bs(html_content, "lxml")

            #get company name
            company_name = False
            s_company_name = soup.find_all(class_= "header-company-title")
            if(len(s_company_name) > 0):
                company_name = s_company_name[0].get_text(strip=True)

            #get ratings
            rating_g = soup.find_all(class_="highcharts-label highcharts-data-label highcharts-data-label-color-undefined")
            for rating_ge in rating_g:
                rating_texts = rating_ge.find_all("text")
                for rating_text in rating_texts:

                    #create a rating dictionary
                    rating_object = {
                        "symbol": symbol,
                        "company_name": company_name,
                        "date": "",
                        "rating": rating_text.get_text(),
                    }
                    ratings.append(rating_object)

            #get rating dates from axis_labels
            axis_labels = soup.find_all(class_="highcharts-axis-labels highcharts-xaxis-labels")
            if(len(axis_labels) > 0):
                date_texts = axis_labels[0].find_all("text")
                # add date to the rating dictionary
                for i in range(len(date_texts) ):
                    ratings[i]["date"] = date_texts[i].get_text()

        # Add rating of current ticker to the result array
        for rating_e in ratings:
            all_ratings.append(rating_e)

    # Save all ratings to a csv file
    with open("./output_ratings.csv", "w", newline="")  as output_file:
        dict_writer = csv.DictWriter(output_file, all_ratings[0].keys())
        dict_writer.writeheader()
        dict_writer.writerows(all_ratings)


def write_to_csv(df_yh):
    df_yh.to_csv("yahoo.dow.jones.full.20201109.csv",
                encoding="utf-8", index=False)


#df.fillna(method='ffill')