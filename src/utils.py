import pandas as pd
#import time as tm
from datetime import datetime, time
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlencode
import json

from telethon.tl.functions.messages import SearchRequest
from telethon.tl.types import InputMessagesFilterEmpty
from telethon import TelegramClient, sync
from telethon import functions, types
from retrying import retry

import pandas as pd


def send_message_telegram(client, user_id, output):
    #destination_channel="https://t.me/{}".format(user)
    #destination_channel="https://t.me/jerrytest"
    entity=client.get_entity(int(user_id))
    #client.send_file(entity=entity,file='screenshot.png',caption=output)
    client.send_message(entity=entity,message=output)

def save_buy_info(buy_info, user, bitcoin_price_eur, btc_to_buy):
    orderId = buy_info['orderId']
    clientOrderId = buy_info['clientOrderId']
    transactTime = buy_info['transactTime']
    quantity_btc = buy_info['origQty']
    quantity_usd = eur_to_usd(buy_info['cummulativeQuoteQty'])
    commission_btc = buy_info['fills'][0]['commission']
    #price_usd = buy_info['fills'][0]['price']
    price_usd = eur_to_usd(bitcoin_price_eur)
    tradeId = buy_info['fills'][0]['tradeId']
    status = 'completed'
    
    output = (transactTime, user, quantity_btc, quantity_usd, commission_btc, price_usd, bitcoin_price_eur, btc_to_buy, orderId, clientOrderId, status)
    data = pd.read_csv('./data.csv')
    
    df = pd.DataFrame(output).T
    df.columns = ['transactTime', "user", "quantity_btc", "quantity_usd", "commission_btc",
              'price_usd', "bitcoin_price_eur", "total_btc", "orderId", "clientOrderId", "status"]
    
    data = data.append(df, sort=False)
    data.to_csv('./data.csv', index=False)


def save_load_info(transactTime, user, bitcoin_price_usd, bitcoin_price_eur, quantity_btc, quantity_usd, btc_to_buy):
    status = 'postponed'
    
    output = (transactTime, user, quantity_btc, quantity_usd, 0, bitcoin_price_usd, bitcoin_price_eur, btc_to_buy, 0, 0, status)
    data = pd.read_csv('./data.csv')
    
    df = pd.DataFrame(output).T
    df.columns = ['transactTime', "user", "quantity_btc", "quantity_usd", "commission_btc",
              'price_usd', "bitcoin_price_eur", "total_btc", "orderId", "clientOrderId", "status"]
    
    data = data.append(df, sort=False)
    data.to_csv('./data.csv', index=False)
    

def usd_to_eur(usd):
    url_eurusd = "https://api.exchangeratesapi.io/latest"
    response = requests.get(url_eurusd)
    soup = BeautifulSoup(response.content, "html.parser")
    dic = json.loads(soup.prettify())

    exchange_rate_1eur_eqto = float(dic['rates']['USD'])
    return float(usd) / exchange_rate_1eur_eqto

def eur_to_usd(eur):
    url_eurusd = "https://api.exchangeratesapi.io/latest"
    response = requests.get(url_eurusd)
    soup = BeautifulSoup(response.content, "html.parser")
    dic = json.loads(soup.prettify())

    exchange_rate_1eur_eqto = float(dic['rates']['USD'])
    return float(eur) * exchange_rate_1eur_eqto

#check the time, snapshot needs to be taken at around 00:00 UTC
def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time
    
def line_prepender(filename, line):
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)
        
        
def create_excel(user, status):
    #status = 'completed' or 'postponed'
    #print('creating excel')
    
    df = pd.read_csv('./data.csv')
    df['date'] = df['transactTime'].apply(lambda x: datetime.fromtimestamp(int(str(x)[:-3])).strftime('%Y-%m-%d %H:%M:%S'))
    df = df.set_index('date')
    df['total_btc_value'] = df['total_btc'] * df['price_usd']
    df3 = df[['user','quantity_btc', 'quantity_usd', 'price_usd', 'bitcoin_price_eur', 'total_btc', 'total_btc_value', 'status']]
    
    
    user_df = df3[df3['user'] == user]
    df_excel = user_df[user_df.status == status]
    
    
    columns = ['quantity_btc',
           'bitcoin_price_eur',
           'price_usd']

    #df_excel = df_excel[columns][::-1]
    df_excel = df_excel[columns]
    df_excel.columns = ['Paid (BTC)', 'BTC Price (EUR)', 'BTC Price (USD)']
    
    df_excel['Exchange In (EUR)'] = df_excel['Paid (BTC)'] * df_excel['BTC Price (EUR)']
    df_excel['Balance (BTC)'] = df_excel['Paid (BTC)'].cumsum()
    df_excel['Paid (EUR)'] = df_excel['Exchange In (EUR)'].cumsum()
    df_excel['Balance (EUR)'] = df_excel['Balance (BTC)'] * df_excel['BTC Price (EUR)']
    df_excel['Balance (USD)'] = df_excel['Balance (BTC)'] * df_excel['BTC Price (USD)']
    df_excel['Average Price Bought (EUR)'] = df_excel['Paid (EUR)'] / df_excel['Balance (BTC)']
    df_excel['Average Price Bought (USD)'] = df_excel['Average Price Bought (EUR)'] * (df_excel['BTC Price (USD)'] / df_excel['BTC Price (EUR)'])
    df_excel['Profit/Loss (EUR)'] = df_excel['Balance (EUR)'] - df_excel['Paid (EUR)']
    df_excel['Profit/Loss Percentage'] = df_excel['Profit/Loss (EUR)'] / df_excel['Paid (EUR)']
    
    cols = ['Paid (BTC)',
        'Exchange In (EUR)',
        'Paid (EUR)',
        'Balance (BTC)',
        'Balance (EUR)',
        'Balance (USD)',
        'BTC Price (EUR)',
        'BTC Price (USD)',
        'Average Price Bought (EUR)',
        'Average Price Bought (USD)',
        'Profit/Loss (EUR)',
        'Profit/Loss Percentage'
    ]

    df_excel = df_excel[cols]
    return df_excel
    

def create_excel_file(user):
    
    #print('create_excel_file')
   
    with pd.ExcelWriter('./excel_files/{}.xlsx'.format(user)) as writer: 
        create_excel('giovanni', 'postponed').to_excel(writer, sheet_name='Postponed')
        create_excel('giovanni', 'completed').to_excel(writer, sheet_name='Completed')
    

