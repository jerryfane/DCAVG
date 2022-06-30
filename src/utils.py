import pandas as pd
#import time as tm
from datetime import datetime, time
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlencode
import json

from pushover import Client
from config import pushover_APIKEY

def send_message_pushover(message, pushover_USERKEY):
    pushover_USERKEY = [pushover_USERKEY]
    client = [Client(key, api_token=pushover_APIKEY) for key in pushover_USERKEY]
    user = client[0]
    user.send_message(message, title='DCAVG')

def get_users(users_path='./datasets/users.csv', data_path='./datasets/data.csv'):
    users = {}
    users_df = pd.read_csv(users_path)

    for user in users_df['username']:
        users[user] = {}
        users[user]['crypto'] = users_df[users_df['username'] == user]['crypto'].values[0]
        users[user]['buy_eur_per_day'] = users_df[users_df['username'] == user]['buy_eur_per_day'].values[0]
        #set true if you want to get the amount of BTC to buy from the amount saved on data.csv
        users[user]['continue_from_last_day'] = users_df[users_df['username'] == user]['continue_from_last_day'].values[0]
        users[user]['btc_to_buy'] = users_df[users_df['username'] == user]['btc_to_buy'].values[0]
        users[user]['API_KEY'] = users_df[users_df['username'] == user]['API_KEY'].values[0]
        users[user]['SECRET_KEY'] = users_df[users_df['username'] == user]['SECRET_KEY'].values[0]
        users[user]['PASSPHRASE'] = users_df[users_df['username'] == user]['PASSPHRASE'].values[0]
        users[user]['telegram_username'] = users_df[users_df['username'] == user]['telegram_username'].values[0]
        users[user]['telegram_id'] = users_df[users_df['username'] == user]['telegram_id'].values[0]
        users[user]['exchange'] = users_df[users_df['username'] == user]['exchange'].values[0]
        users[user]['increase_buy'] = users_df[users_df['username'] == user]['increase_buy'].values[0]
        users[user]['pushover_userkey'] = users_df[users_df['username'] == user]['pushover_userkey'].values[0]


    for user in users:
        if users[user]['continue_from_last_day'] == True:
            data = pd.read_csv(data_path)
            try:
                btc_to_buy = data[data['user'] == user]['total_btc'].values[-1]
            except:
                btc_to_buy = users[user]['btc_to_buy']
            users[user]['btc_to_buy'] = btc_to_buy

    return users



def usd_to_eur(usd):
    url_eurusd = "https://api.exchangeratesapi.io/latest?access_key=ec10cc589293d5f5da39e53ca30c0f7d"
    response = requests.get(url_eurusd)
    soup = BeautifulSoup(response.content, "html.parser")
    dic = json.loads(soup.prettify())

    exchange_rate_1eur_eqto = float(dic['rates']['USD'])
    return float(usd) / exchange_rate_1eur_eqto

def eur_to_usd(eur):
    url_eurusd = "http://api.exchangeratesapi.io/latest?access_key=ec10cc589293d5f5da39e53ca30c0f7d"
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


def create_excel(user, status, data_path='./datasets/data.csv'):
    #status = 'completed' or 'postponed'
    #print('creating excel')

    df = pd.read_csv(data_path)
    df['date'] = df['transactTime'].apply(lambda x: datetime.fromtimestamp(int(str(x)[:-3])/100).strftime('%Y-%m-%d %H:%M:%S'))
    df = df.set_index('date')
    df['total_crypto_value'] = df['total_crypto'] * df['price_usd']
    df3 = df[['user', 'quantity_crypto', 'quantity_usd', 'price_usd', 'crypto_price_eur', 'total_crypto', 'total_crypto_value', 'status']]


    user_df = df3[df3['user'] == user]
    df_excel = user_df[user_df.status == status]


    columns = ['quantity_crypto',
               'crypto_price_eur',
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

    cols = [
        'Paid (BTC)',
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


def create_excel_file(user, data_path):


    with pd.ExcelWriter('./excel_files/{}.xlsx'.format(user)) as writer:
        create_excel(user, 'postponed', data_path).to_excel(writer, sheet_name='Postponed')
        create_excel(user, 'completed', data_path).to_excel(writer, sheet_name='Completed')
