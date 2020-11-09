import requests
import bs4

def get_soup(url):

    page = requests.get(url)

    soup = bs4.BeautifulSoup(page.content, 'lxml')

    return soup

soup = get_soup('https://finance.yahoo.com/quote/%5EDJI/components?p=%5EDJI')

divs = soup.find_all('div')
