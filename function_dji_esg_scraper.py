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
import os.path
import time

# define user-agent
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Pragma': 'no-cache',
    'Referrer': 'https://google.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240 Safari/537.36'
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
    frame.loc[len(frame.index)] = ['^DJI', 'Dow Jones Industrial']  

    return frame

def download_yahoo_stock_htmlfile(stock_index):
    #crate a new folder for html files
    os.makedirs("./stock_html", exist_ok=True)

    driver = webdriver.Chrome(ChromeDriverManager().install())
    # get the financial data from the previous 5 years / weekly
    for symbol in stock_index.symbol:
        # stock data
        url = ('https://finance.yahoo.com/quote/{}/history?period1=1449187200&period2=1607040000&interval=1wk&filter=history&frequency=1wk&includeAdjustedClose=true'.format(symbol))
        driver.get(url)
        print("Crawling yahoo stock: " + symbol)

        ScrollNumber = 6
        for i in range(1,ScrollNumber):
            driver.execute_script("window.scrollTo(1,50000)")
            time.sleep(2)

        with open("./stock_html/" + symbol + ".html", "w") as full_html:
            full_html.write(driver.page_source)
    
    driver.quit()

def get_stock_data(stock_index):

    # create an empty pd dataframe
    df_dji = pd.DataFrame()

    # get the financial data from the previous 5 years / monthly
    for symbol, company in zip(stock_index.symbol, stock_index.company):
        
        filename = "./stock_html/" + symbol + ".html"

        if(os.path.isfile(filename) == False):
            print("Error: File for stock-data: " + symbol + " not found.")
            continue
        else:
            page = open(filename, "r",  encoding='unicode_escape')
            soup = bs(page, "lxml")
            tables = soup.find_all('table')
            table = pd.read_html(str(tables))[0]
            df_yahoo = pd.DataFrame(table)

            #clean up stock table
            df_yahoo = df_yahoo.iloc[:-1, [0, 4, 5]] #remove the last row (description) and non-necessary columns
            df_yahoo.rename(columns={'Date':'date', 'Close*':'stock', 'Adj Close**':'adj_stock'}, inplace=True) #rename columns
            df_yahoo = df_yahoo[pd.to_numeric(df_yahoo['stock'], errors='coerce').notnull()] #remove non-numeric values (splits & dividends)

            #change date format
            df_yahoo['date'] = df_yahoo['date'].str.replace(",", "")
            df_yahoo['date'] =  pd.to_datetime(df_yahoo['date'], format='%b %d %Y')
            
            #create a monthly
            df_yahoo['month_year'] = df_yahoo['date'].dt.strftime('%Y-%m')
            #change the notion of date
            df_yahoo['date'] =  df_yahoo['date'].dt.strftime('%Y-%m-%d')



            
            #add company name and symbol
            df_yahoo['company'] = company
            df_yahoo['symbol'] = symbol

                
            # concat to empty pandas df
            df_dji = pd.concat([df_dji, df_yahoo], ignore_index=True, sort=True)

    return df_dji


def download_msci_esg_ratings_htmlfile(stock_index):
    #crate a new folder for html files
    os.makedirs("./esg_html", exist_ok=True)

    # old url 'https://www.msci.com/esg-ratings'
    msci_url = "https://www.msci.com/our-solutions/esg-investing/esg-ratings/esg-ratings-corporate-search-tool" 

    # initialize selenium webdriver
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    #chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

    #scrape esg rating for all constituents
    for symbol in stock_index.symbol:
        print("Crawling ESG Ticker: " + symbol)
        # go to search page
        driver.get(msci_url)
        element = driver.find_element_by_id("_esgratingsprofile_keywords")
        # enter Ticker into search field
        element.send_keys(symbol)
        element.send_keys(" ")
        time.sleep(1)

        #select first search result
        element.send_keys(Keys.ARROW_DOWN)
        time.sleep(0.5)
        element.send_keys(Keys.RETURN)
        time.sleep(1.5)

        #save full html page with esg rataing to be processed later
        with open("./esg_html/" + symbol + ".html", "w") as full_html:
            full_html.write(driver.page_source)

    #close webdriver gracefully
    driver.quit()


def get_esg_from_html(stock_index):
    all_ratings = []
    
    for symbol in stock_index.symbol:
        # result array with esg ratigns for current ticker
        ratings = []

        # open saved html file
        filename = "./esg_html/" + symbol + ".html"
        if(os.path.isfile(filename) == False):
            print("Error: File for ticker: " + symbol + " not found.")
            continue
        else:
            f = open(filename, "r",  encoding='unicode_escape')
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
        
        #change format to a pd.DataFrame
        df_esg = pd.DataFrame(all_ratings)

    #converte date (yyyy-mm)
    df_esg['date'] = pd.to_datetime(df_esg['date'], format= "%b-%y")#dt.to_period('M')
    df_esg['month_year'] =  df_esg['date'].dt.strftime('%Y-%m')

    #return esg frame
    return df_esg


def join_dji_esg(df_dji, df_esg):
    #outer on symbol and date (outer join)
    df_dji_esg = pd.merge(df_dji, df_esg[['symbol','month_year','rating']], how='outer', on=['symbol', 'month_year'])

    #sort values based on date/month_year ascending
    df_dji_esg= df_dji_esg.sort_values(by=['symbol','month_year','date'],na_position='first')

    #fill forward ratings
    df_dji_esg['rating'] = df_dji_esg.groupby(['symbol'], sort=False)['rating'].fillna(method='ffill')

    #drop rating entries without stock data
    df_dji_esg.dropna(subset=['stock'], inplace=True)

    #return joined frame
    return df_dji_esg


def write_to_csv(df_dji_esg):
    df_dji_esg.to_csv("df_dji_esg.csv",
                encoding="utf-8", index=False)