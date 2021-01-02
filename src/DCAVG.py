import numpy as np
import pandas as pd
import time as tm
from datetime import datetime, time
from bs4 import BeautifulSoup

from Binance import BinanceException, Binance
from Coinbase import CoinbasePro
from secrets import api_id, api_hash #insert here your Telegram API keys
from config import users
from utils import *


def main(client):
    #wait 1 day
    #tm.sleep(60*60*24)

    #buy at 5PM to 5:30PM UTC, check here if it is time to buy
    is_it_time = is_time_between(time(17,59), time(18,30))

    #if is it time to buy, proceed
    if is_it_time:
        print(datetime.utcnow(),is_it_time)
        line_prepender('log.txt', str(datetime.utcnow())+' '+str(is_it_time))


        for user in users:
            exchange_name = users[user]['exchange'].lower()
            exchange = exchange_dict[user]
            telegram_id = telegram_id_dict[user]

            #check price of Bitcoin, buy in USDT
            #bitcoin_price_usd = float(binance.get_binance_price('BTCUSDT')['price'])
            #bitcoin_price_eur = usd_to_eur(bitcoin_price_usd)

            #check price of Bitcoin, buy in EUR
            bitcoin_price_eur = float(exchange.get_price('BTCEUR')['price'])
            bitcoin_price_usd = eur_to_usd(bitcoin_price_eur)

            buy_eur_per_day = users[user]['buy_eur_per_day']
            if users[user]['continue_from_last_day'] == True:
                data_temp = pd.read_csv('./data.csv')
                try:
                    btc_to_buy = data_temp[data_temp['user'] == user]['total_btc'].values[-1]
                except:
                    #initialize user
                    btc_to_buy = users[user]['btc_to_buy']
                users[user]['btc_to_buy'] = btc_to_buy
                del data_temp
            else:
                btc_to_buy = users[user]['btc_to_buy']

            #calculate how many bitcoin to buy
            btc_to_buy += round((buy_eur_per_day / bitcoin_price_eur),6)
            btc_to_buy_value = btc_to_buy*bitcoin_price_eur
            print(btc_to_buy)
            print(btc_to_buy_value)

            #save load info
            transactTime = exchange.get_servertime()
            save_load_info(transactTime, user, bitcoin_price_usd, bitcoin_price_eur, round((buy_eur_per_day / bitcoin_price_eur),6), round((buy_eur_per_day / bitcoin_price_eur),6)*bitcoin_price_usd, btc_to_buy)

            #if amount_btc*price < 10 EUR

            if btc_to_buy*bitcoin_price_eur < 10:
                #continue to next user
                continue
            elif exchange_name == 'coinbase' and btc_to_buy < 0.001:
                #continue to next user
                continue
            else:
                #buy bitcoin
                btc_to_buy = round(btc_to_buy,6)
                print(btc_to_buy)


                try:
                    buy_info = exchange.buy_BTC('MARKET', btc_to_buy)
                    #reset btc_to_buy
                    btc_to_buy = 0
                    save_buy_info(buy_info, user, bitcoin_price_eur, btc_to_buy, transactTime, exchange=exchange_name)
                    message_str = """We just bough some Bitcoin for you!\nCheck your {} account.""".format(exchange_name.capitalize())
                    send_message_telegram(client, telegram_id, "User: {}\n".format(user) + message_str)
                except Exception as e:
                    print(e)
                    send_message_telegram(client, telegram_id, "User: {}\n".format(user) + str(e))
                    #if account has insufficient balance, send message to user
                    #if 'Account has insufficient balance' in str(e):
                    #    print('send message to user')




        #once done all users, wait 30 minutes
        tm.sleep(60*30)

        #restart
        main(client)
    else:
        print(datetime.utcnow(),is_it_time)
        line_prepender('log.txt', str(datetime.utcnow())+' '+str(is_it_time))
        #wait 30 minutes
        tm.sleep(60*30)

        #restart
        main(client)



exchange_dict = {}
telegram_id_dict = {}

client = TelegramClient('DCAVG_session', api_id, api_hash).start()

for user in users:
    API_KEY = users[user]['API_KEY']
    SECRET_KEY = users[user]['SECRET_KEY']
    PASSPHRASE = users[user]['PASSPHRASE']
    if users[user]['exchange'].lower() == 'binance':
        exchange = Binance(API_KEY, SECRET_KEY)
        exchange_dict[user] = exchange
    elif users[user]['exchange'].lower() == 'coinbase':
        exchange = CoinbasePro(API_KEY, SECRET_KEY, PASSPHRASE)
        exchange_dict[user] = exchange

    telegram_id = users[user]['telegram_id']
    telegram_id_dict[user] = telegram_id

main(client)
