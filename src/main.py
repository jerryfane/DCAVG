import numpy as np
import pandas as pd
import time as tm
from datetime import datetime, time

from Binance import BinanceException, Binance
from Coinbase import CoinbasePro
from utils import *

from User import User

def load_User(username, users):
    crypto = users[username]['crypto']
    # telegram_username = users[username]['telegram_username']
    # telegram_id = users[username]['telegram_id']
    pushover_userkey = users[username]['pushover_userkey']
    exchange_name = users[username]['exchange']
    buy_eur_per_day = users[username]['buy_eur_per_day']
    continue_from_last_day = users[username]['continue_from_last_day']
    increase_buy = users[username]['increase_buy']
    API_KEY = users[username]['API_KEY']
    SECRET_KEY = users[username]['SECRET_KEY']
    PASSPHRASE = users[username]['PASSPHRASE']

    user = User(username,
                 # telegram_username,
                 # telegram_id,
                 pushover_userkey,
                 exchange_name,
                 buy_eur_per_day,
                 continue_from_last_day,
                 increase_buy,
                 API_KEY,
                 SECRET_KEY,
                 PASSPHRASE)
    return crypto, user

def main():

    is_it_time = is_time_between(time(9,59), time(18,30))

    #if is it time to buy, proceed
    if is_it_time:
        print(datetime.utcnow(),is_it_time)
        line_prepender('./datasets/log.txt', str(datetime.utcnow())+' '+str(is_it_time))

        from utils import get_users
        users = get_users()
        for username in users:
            crypto, user = load_User(username, users)
            print('Working for {} on {}'.format(username, crypto))
            user.buy(crypto=crypto)

        #once done all users, wait 30 minutes
        tm.sleep(60*30)

        #restart
        main()

    else:
        print(datetime.utcnow(),is_it_time)
        line_prepender('./datasets/log.txt', str(datetime.utcnow())+' '+str(is_it_time))
        #wait 30 minutes
        tm.sleep(60*30)

        #restart
        main()


if __name__ == "__main__":
    main()
