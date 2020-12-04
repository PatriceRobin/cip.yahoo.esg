def get_yahoo_df_sustainability(stock_index):
    df_sustainable = pd.DataFrame()
    # create an empty pd dataframe
    df_sustainable['symbol'] = stock_index.symbol

    for symbol in stock_index.symbol:
        #dow jones as an index has no ESG score
        try:
            #sustainability score
            frame = pd.DataFrame()
            url = ('https://finance.yahoo.com/quote/{}/sustainability?p={}'.format(symbol, symbol)) #access the sustainability page of every company in the dow jones industrial index
            #environment
            frame['environment'] = get_soup(url=url).find('div', attrs={"data-reactid": "35"}).text
            #social socre
            frame['social'] = get_soup(url=url).find('div', attrs={"data-reactid": "43"}).text
            #governance score
            frame['governance'] = get_soup(url=url).find('div', attrs={"data-reactid": "50"}).text
            #overall substainability score
            #frame['riskscore'] = get_soup(url=url).find('div', attrs={"class":"Fz(36px) Fw(600) D(ib) Mend(5px)"}).text
        except:
            print("Error: yahoo sunstainability score: " + symbol + " not found.")
            continue

    # concat to empty pandas df
    df_sustainable = pd.concat([df_sustainable, frame], ignore_index=True, sort=True)
    
    return df_sustainable