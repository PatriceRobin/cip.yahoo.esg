from yahoo_finance import get_stock_index, get_stock_data, write_to_csv, get_esg_from_html

def scrap_stock():
    table = get_stock_index(url='https://finance.yahoo.com/quote/%5EDJI/components?p=%5EDJI')
    stock_data = get_stock_data(stock_index=table)
    get_esg_from_html(stock_index=table)
    write_to_csv(df_yh=stock_data)
    
if  __name__  == "__main__":
    scrap_stock()
