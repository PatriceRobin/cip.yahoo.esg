#import packages for yahoo
import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import re

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import os.path
import time

stock_index = ['AAPL', 'DOW']

def download_yahoo_stock_htmlfile(stock_index):
    #crate a new folder for html files
    os.makedirs("./stock_html", exist_ok=True)

    driver = webdriver.Chrome(ChromeDriverManager().install())
    # get the financial data from the previous 5 years / weekly
    for symbol in stock_index:#, stock_index.company):
        # stock data
        url = ('https://finance.yahoo.com/quote/AAPL/history?period1=1449187200&period2=1607040000&'\
            'interval=1wk&filter=history&frequency=1wk&includeAdjustedClose=true'.format(symbol))
        driver.get(url)
        print("Crawling yahoo stock: " + symbol)

        ScrollNumber = 5
        for i in range(1,ScrollNumber):
            driver.execute_script("window.scrollTo(1,50000)")
            time.sleep(0.3)

        with open("./stock_html/" + symbol + ".html", "w") as full_html:
            full_html.write(driver.page_source)
    
    driver.quit()


def scrape(stock_index):
    for symbol in stock_index:

        filename = "./stock_html/" + symbol + ".html"

        if(os.path.isfile(filename) == False):
            print("Error: File for ticker: " + symbol + " not found.")
            continue
        else:
            page = open(filename, "r",  encoding='unicode_escape')
            soup = bs(page, "lxml")
            tables = soup.find_all('table')
            table = pd.read_html(str(tables))[0]
            frame = pd.DataFrame(table)

            print(frame)

download_yahoo_stock_htmlfile(stock_index)
scrape(stock_index)