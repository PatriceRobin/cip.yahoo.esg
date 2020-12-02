from yahoo_esg import get_stock_index, get_stock_data, write_to_csv, get_esg_from_html, join_dowjones_esg

def scrap_stock():
    table = get_stock_index(url='https://finance.yahoo.com/quote/%5EDJI/components?p=%5EDJI')
    stock_data = get_stock_data(stock_index=table)
    esg_data = get_esg_from_html(stock_index=table)
    stock_esg_data = join_dowjones_esg(df_dowjones=stock_data,df_esg=esg_data)
    write_to_csv(df_dowjones_esg_clean=stock_esg_data)
    
if  __name__  == "__main__":
    scrap_stock()
