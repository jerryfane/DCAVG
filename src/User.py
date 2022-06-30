import numpy as np
import pandas as pd
import time as tm
from datetime import datetime, time
#from bs4 import BeautifulSoup

from Binance import BinanceException, Binance
from Coinbase import CoinbasePro
from config import pushover_APIKEY
from utils import *

import warnings
warnings.filterwarnings("ignore")

class User():

    def __init__(self,
                 username,
                 # telegram_username,
                 # telegram_id,
                 pushover_userkey,
                 exchange_name,
                 buy_eur_per_day,
                 continue_from_last_day,
                 increase_buy,
                 API_KEY,
                 SECRET_KEY,
                 PASSPHRASE
                ):

        self.username = username
        # self.telegram_username = telegram_username
        # self.telegram_id = telegram_id
        self.pushover_userkey = pushover_userkey
        self.exchange_name = exchange_name.lower()
        self.buy_eur_per_day = buy_eur_per_day

        self.API_KEY = API_KEY
        self.SECRET_KEY = SECRET_KEY
        self.PASSPHRASE = PASSPHRASE

        self.continue_from_last_day = continue_from_last_day
        self.increase_buy = increase_buy

        # Init
        self.amount_to_buy = None
        self.exchange = None

        self.data_path = './datasets/data.csv'
        self.users_path = './datasets/users.csv'

        # Manually add crypto pairs here
        self.crypto_pairs = {'BTC': 'BTCEUR', 'ETH': 'ETHEUR'}

        # Run
        self._load_exchange()

    def _load_exchange(self):

        if self.exchange_name == 'binance':
            exchange = Binance(self.API_KEY, self.SECRET_KEY)
        elif self.exchange_name == 'coinbase':
            exchange = CoinbasePro(self.API_KEY, self.SECRET_KEY, self.PASSPHRASE)

        self.exchange = exchange


    def measure_amount_to_buy(self,
                              continue_from_last_day,
                              amount_to_buy,
                              crypto='BTC'):


        if continue_from_last_day:
            data = pd.read_csv(self.data_path)
            try:
                filter_ = (data.user == self.username) & (data.crypto == crypto)
                amount_to_buy = data[filter_]['total_crypto'].values[-1]
            except:
                pass

        del data
        self.amount_to_buy = amount_to_buy
        return amount_to_buy


    def get_crypto_prices(self, crypto='BTC'):
        data_temp = pd.read_csv(self.data_path)

        pair = self.crypto_pairs[crypto]

        filter_ = (data_temp.user == self.username) & (data_temp.crypto == crypto)
        try:
            last_crypto_price_eur = data_temp[filter_]['crypto_price_eur'].values[-1] # get last value of crypto price
        except:
            last_crypto_price_eur = float(self.exchange.get_price(pair)['price'])

        # check crypto price from Exchange API
        crypto_price_eur = float(self.exchange.get_price(pair)['price'])
        crypto_price_usd = eur_to_usd(crypto_price_eur)

        return last_crypto_price_eur, crypto_price_eur, crypto_price_usd

    def _save_load_info(self,
                        crypto_price_eur,
                        buy_eur,
                        amount_to_buy,
                        crypto_price_usd,
                        crypto='BTC'):

        def save_load_info(transactTime, user, crypto, crypto_price_usd, crypto_price_eur, quantity_crypto, quantity_usd, amount_to_buy):
            status = 'postponed'

            output = (transactTime, user, crypto, quantity_crypto, quantity_usd, 0, crypto_price_usd, crypto_price_eur, amount_to_buy, 0, 0, status)
            data = pd.read_csv(self.data_path)

            df = pd.DataFrame(output).T
            df.columns = ['transactTime', "user", "crypto", "quantity_crypto", "quantity_usd", "commission_crypto",
                      'price_usd', "crypto_price_eur", "total_crypto", "orderId", "clientOrderId", "status"]

            data = data.append(df, sort=False)
            data.to_csv(self.data_path, index=False)


        transactTime = self.exchange.get_servertime()
        save_load_info(transactTime, self.username, crypto, crypto_price_usd, crypto_price_eur, round((buy_eur / crypto_price_eur),6), round((buy_eur / crypto_price_eur),6)*crypto_price_usd, amount_to_buy)

    def _send_client_message(self, amount_to_buy, crypto_price_eur, crypto):

        def get_stats(crypto_price_eur):
            data = pd.read_csv(self.data_path)
            data['spent'] = data.quantity_crypto * data.crypto_price_eur

            filter_ = (data.user == self.username) & (data.crypto == crypto) & (data.status == 'completed')
            data = data[filter_]

            total_bought = data[filter_].quantity_crypto.sum()
            total_spent = round(data[filter_].spent.sum(),2)
            current_value = round(total_bought * crypto_price_eur, 2)
            average_price = round(total_spent / total_bought, 2)
            ROI = round((current_value - total_spent) / total_spent * 100,2)

            return total_bought, total_spent, current_value, average_price, ROI

        total_bought, total_spent, current_value, average_price, ROI = get_stats(crypto_price_eur)

        message_str = """We just bought some crypto for you!\nCheck your {} account.\n\nCrypto: {}\nAmount bought: {}\nPrice: {}EUR\nSpent: {}EUR\n\nStatistics:\nTotal {} bought: {}\nTotal spent: {}EUR\nCurrent total value: {}EUR\nAverage price bought: {}EUR\nROI: {}%""".format(self.exchange_name, crypto, amount_to_buy, round(crypto_price_eur, 3), round(crypto_price_eur*amount_to_buy, 3), crypto, total_bought, total_spent, current_value, average_price, ROI)

        send_message_pushover("User: {}\n".format(self.username) + message_str, self.pushover_userkey)

    def _send_buy_order(self,
                        amount_to_buy,
                        crypto_price_eur,
                        crypto='BTC'):

        def save_buy_info(buy_info, user, crypto, crypto_price_eur, amount_to_buy, transactTime, exchange='binance'):
            if exchange == 'binance':
                orderId = buy_info['orderId']
                clientOrderId = buy_info['clientOrderId']
                #transactTime = buy_info['transactTime']
                quantity_crypto = buy_info['origQty']
                quantity_usd = eur_to_usd(buy_info['cummulativeQuoteQty'])
                commission_crypto = buy_info['fills'][0]['commission']
                #price_usd = buy_info['fills'][0]['price']
                price_usd = eur_to_usd(crypto_price_eur)
                tradeId = buy_info['fills'][0]['tradeId']
                status = 'completed'

            elif exchange == 'coinbase':
                orderId = buy_info['order_id'].values[0]
                clientOrderId = buy_info['order_id'].values[0]
                #transactTime = buy_info['created_at'].values[0]
                quantity_crypto = buy_info['size'].values[0]
                quantity_usd = buy_info['usd_volume'].values[0]
                commission_crypto = float(buy_info['fee'].values[0]) / crypto_price_eur
                price_usd = eur_to_usd(crypto_price_eur)
                tradeId = buy_info['trade_id'].values[0]
                status = 'completed'

            output = (transactTime, user, crypto, quantity_crypto, quantity_usd, commission_crypto, price_usd, crypto_price_eur, amount_to_buy, orderId, clientOrderId, status)
            data = pd.read_csv(self.data_path)

            df = pd.DataFrame(output).T
            df.columns = ['transactTime', "user", "crypto", "quantity_crypto", "quantity_usd", "commission_crypto",
                      'price_usd', "crypto_price_eur", "total_crypto", "orderId", "clientOrderId", "status"]

            data = data.append(df, sort=False)
            data.to_csv(self.data_path, index=False)

        if crypto not in self.crypto_pairs:
            return 'Crypto still not configured'

        transactTime = self.exchange.get_servertime()
        amount_to_buy = round(amount_to_buy, 4) if crypto == 'ETH' else amount_to_buy
        buy_info = self.exchange.buy_crypto('MARKET', amount_to_buy, self.crypto_pairs[crypto])

        amount_to_buy = 0
        save_buy_info(buy_info, self.username, crypto, crypto_price_eur, amount_to_buy, transactTime, exchange=self.exchange_name)

    def buy(self,
            amount_to_buy=0,
            crypto='BTC'):

        last_crypto_price_eur, crypto_price_eur, crypto_price_usd = self.get_crypto_prices(crypto=crypto)

        # temporary config, may be better defined
        buy_eur = self.buy_eur_per_day

        amount_to_buy = self.measure_amount_to_buy(self.continue_from_last_day,
                              amount_to_buy,
                              crypto)

        if self.increase_buy and crypto_price_eur < last_crypto_price_eur: #increase the amount of crypto to buy if the price decreased from last time
            amount_to_buy += round((buy_eur / crypto_price_eur),6) * (1+abs((crypto_price_eur - last_crypto_price_eur) / last_crypto_price_eur))
        else:
            amount_to_buy += round((buy_eur / crypto_price_eur),6)

        crypto_to_buy_value = amount_to_buy*crypto_price_eur

        print('Buying {} {}, for {} EUR'.format(amount_to_buy, crypto, crypto_to_buy_value))

        # save buying info
        self._save_load_info(crypto_price_eur,
                        buy_eur,
                        amount_to_buy,
                        crypto_price_usd,
                        crypto=crypto)

        # minimum to buy
        if amount_to_buy*crypto_price_eur < 10:
            pass
        elif self.exchange_name == 'coinbase' and amount_to_buy < 0.001 and crypto == 'BTC':
            pass # do nothing
        else:
            try:
                # buy crypto
                amount_to_buy = round(amount_to_buy,5)
                self._send_buy_order(amount_to_buy, crypto_price_eur, crypto)
                self._send_client_message(amount_to_buy, crypto_price_eur, crypto)
            except Exception as e:
                # example account don't have enough balance
                print(e)
                send_message_pushover("User: {}\n".format(self.username) + str(e), self.pushover_userkey)
