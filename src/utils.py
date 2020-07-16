import pandas as pd
import time
from datetime import datetime
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

