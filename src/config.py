import pandas as pd

buy_eur_per_day = 4.00
btc_to_buy = 0

#set true if you want to get the amount of BTC to buy from the amount saved on data.csv
continue_from_last_day = True


if continue_from_last_day:
    data = pd.read_csv('./data.csv')
    btc_to_buy = data['total_btc'].values[-1]
