from function_dji_esg_scraper import(
    get_stock_index,
    download_yahoo_stock_htmlfile,
    get_stock_data,
    write_to_csv,
    get_esg_from_html,
    join_dji_esg,
    download_msci_esg_ratings_htmlfile
    )

def scrap_stock():
    table = get_stock_index(url='https://finance.yahoo.com/quote/%5EDJI/components?p=%5EDJI')
    #download_yahoo_stock_htmlfile(stock_index=table)
    stock_data = get_stock_data(stock_index=table)
    #download_msci_esg_ratings_htmlfile(stock_index=table)
    esg_data = get_esg_from_html(stock_index=table)
    stock_esg_data = join_dji_esg(df_dji=stock_data,df_esg=esg_data)
    write_to_csv(df_dji_esg=stock_esg_data)
    
if  __name__  == "__main__":
    scrap_stock()
