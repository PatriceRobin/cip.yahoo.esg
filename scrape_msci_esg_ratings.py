# Steps before using this script
# 1: Install Packages
#    pip install webdriver_manager
#    pip install BeautifulSoup
#    pip install selenium
#    pip install lxml

from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager

from selenium import webdriver
import time
import os.path
import csv



def get_index_constituents():
    return ["BA" , "CSCO" ,"KO", "MCD", "TRV","CRM", "AMGN","AAPL", "DIS","MSFT", "MRK","PG", "CVX","V", "WBA","MMM", "VZ","DOW", "JPM", "IBM","INTC", "GS","HON","NKE","CAT","HD","WMT","AXP", "UNH","JNJ"]


def extract_rating_from_htmlfile(ticker_list):
    # result array with all esg ratigns
    all_ratings = []

    for ticker in ticker_list:
        # result array with esg ratigns for current ticker
        ratings = []

        # open saved html file
        filename = "./data/" + ticker + ".html"
        if(os.path.isfile(filenmae) == False):
            print("Error: File for ticker: " + ticker + " not found.")
            continue
        else:
            f = open(filenmae, "r")
            html_content = f.read()
            soup = BeautifulSoup(html_content, "lxml")

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
                        "ticker": ticker,
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
    with open('./data/output_ratings.csv', 'w', newline='')  as output_file:
        dict_writer = csv.DictWriter(output_file, all_ratings[0].keys())
        dict_writer.writeheader()
        dict_writer.writerows(all_ratings)


def download_msci_esg_ratings_htmlfile():

    msci_url = "https://www.msci.com/our-solutions/esg-investing/esg-ratings/esg-ratings-corporate-search-tool" # old url 'https://www.msci.com/esg-ratings'


    # get index constituents
    index_constituents = get_index_constituents()

    # initialize selenium webdriver
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    #chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options )

    #scrape esg rating for all constituents
    for index_constituent in index_constituents:
        print("Crawling Ticker: " + index_constituent)
        # 1: Go to search page
        driver.get(msci_url)
        element = driver.find_element_by_id("_esgratingsprofile_keywords")
        # 2: Enter Ticker into search field
        element.send_keys(index_constituent)
        element.send_keys(" ")
        time.sleep(1)
        # 3: Select first search result
        element.send_keys(Keys.ARROW_DOWN)
        time.sleep(0.5)
        element.send_keys(Keys.RETURN)
        time.sleep(1.5)

        # 4: Save full html page with esg rataing to be processed later
        with open("./data/" + index_constituent + ".html", "w") as f:
            f.write(driver.page_source)

    # close webdriver gracefully
    driver.quit()

def start_scraping():
    #download_msci_esg_ratings_htmlfile()
    extract_rating_from_htmlfile(get_index_constituents())

start_scraping()