import pandas as pd
#import time as tm
from datetime import datetime, time
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlencode
import json

import pandas as pd

def save_buy_info(buy_info, bitcoin_price_eur, btc_to_buy):
    orderId = buy_info['orderId']
    clientOrderId = buy_info['clientOrderId']
    transactTime = buy_info['transactTime']
    quantity_btc = buy_info['origQty']
    quantity_usd = buy_info['cummulativeQuoteQty']
    commission_btc = buy_info['fills'][0]['commission']
    price_usd = buy_info['fills'][0]['price']
    tradeId = buy_info['fills'][0]['tradeId']
    status = 'completed'
    
    output = (transactTime, quantity_btc, quantity_usd, commission_btc, price_usd, bitcoin_price_eur, btc_to_buy, orderId, clientOrderId, status)
    data = pd.read_csv('./data.csv')
    
    df = pd.DataFrame(output).T
    df.columns = ['transactTime', "quantity_btc", "quantity_usd", "commission_btc",
              'price_usd', "bitcoin_price_eur", "total_btc", "orderId", "clientOrderId", "status"]
    
    data = data.append(df, sort=False)
    data.to_csv('./data.csv', index=False)


def save_load_info(transactTime, bitcoin_price_usd, bitcoin_price_eur, quantity_btc, quantity_usd, btc_to_buy):
    status = 'postponed'
    
    output = (transactTime, quantity_btc, quantity_usd, 0, bitcoin_price_usd, bitcoin_price_eur, btc_to_buy, 0, 0, status)
    data = pd.read_csv('./data.csv')
    
    df = pd.DataFrame(output).T
    df.columns = ['transactTime', "quantity_btc", "quantity_usd", "commission_btc",
              'price_usd', "bitcoin_price_eur", "total_btc", "orderId", "clientOrderId", "status"]
    
    data = data.append(df, sort=False)
    data.to_csv('./data.csv', index=False)
    

def usd_to_eur(usd):
    url_eurusd = "https://api.exchangeratesapi.io/latest"
    response = requests.get(url_eurusd)
    soup = BeautifulSoup(response.content, "html.parser")
    dic = json.loads(soup.prettify())

    exchange_rate_1eur_eqto = dic['rates']['USD']
    return usd / exchange_rate_1eur_eqto

def eur_to_usd(eur):
    url_eurusd = "https://api.exchangeratesapi.io/latest"
    response = requests.get(url_eurusd)
    soup = BeautifulSoup(response.content, "html.parser")
    dic = json.loads(soup.prettify())

    exchange_rate_1eur_eqto = dic['rates']['USD']
    return eur * exchange_rate_1eur_eqto

#check the time, snapshot needs to be taken at around 00:00 UTC
def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time

