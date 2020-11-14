import requests
import pandas as pd
from bs4 import BeautifulSoup as bs

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


year = list(range(1977,2021))

# create an empty pd dataframe
box_office = pd.DataFrame()

# get Dow Jones Industrial companies
for year in year:
    url = "https://www.boxofficemojo.com/year/world/{}/".format(year)
    page = requests.get(url, headers).text
    soup = bs(page, "lxml")
    table = soup.find_all('table')
    df = pd.read_html(str(table))[0]
    df = pd.DataFrame(df)
    df

    box_office= pd.concat([box_office, df], ignore_index=True, ascending=False)

print(box_office)