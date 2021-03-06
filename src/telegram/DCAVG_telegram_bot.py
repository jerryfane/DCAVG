import numpy as np
import pandas as pd
import time as tm
from datetime import datetime, time
from bs4 import BeautifulSoup
from telethon import events

import sys
sys.path.append('../')

from Binance import BinanceException, Binance
from secrets import api_id, api_hash #insert here your Binance API keys
from config import get_users
from utils import *


client = TelegramClient('DCAVG_bot_session', api_id, api_hash).start()
users_path = '../datasets/users.csv'
data_path = '../datasets/data.csv'

users = get_users(users_path, data_path)

@client.on(events.NewMessage())
async def my_event_handler(event):
    sender = await event.get_sender()
    print(sender.username, str(event.chat_id))

    if 'start' in event.text:
        users = pd.read_csv(users_path)
        if sender.username in list(users.telegram_username):
            rows = users[users.telegram_username == sender.username].index
            for row_index in rows:
                users.loc[row_index,'telegram_id'] = event.chat_id
            users.to_csv(users_path, index=False)
            await event.respond('Your data has been loaded, you will now receive eventual notifications here!')
        else:
            await event.respond('You are still not registered on DCAVG, please sign up at ///.com')
    #name = utils.get_display_name(sender)
    #print(sender, 'said', event.text, '!')
    #return

    if 'report' in event.text.lower():
        users = pd.read_csv(users_path)
        if sender.username in list(users.telegram_username):
            rows = users[users.telegram_username == sender.username]
            user = rows.username.values[0]
            create_excel_file(user, data_path)
            await event.respond('Your excel report is coming ;)')
            await client.send_file(event.chat_id, './excel_files/{}.xlsx'.format(user))

    if 'reset_bitcoin_amount' in event.text.lower():
        users = pd.read_csv(users_path)
        if sender.username in list(users.telegram_username):
            data = pd.read_csv(data_path)
            data = data.append([{'user': sender.username, 'total_btc':0.0, 'status':'reset_bitcoin_amount'}], ignore_index=True)
            data.to_csv(data_path, index=False)
            await event.respond('Your amount of Bitcoin to buy has been reset to zero')

    if 'set_bitcoin_to_buy' in event.text.lower():
        users = pd.read_csv(users_path)
        print(float(event.text.split(' ')[-1]))
        if sender.username in list(users.telegram_username):
            index = df[df.username == sender.username].index[0]
            amount = float(event.text.split(' ')[-1])
            users.loc[index,'buy_eur_per_day'] = amount
            users.to_csv(users_path, index=False)
            await event.respond('Your amount of Bitcoin to buy each day has been set to {} euro per day'.format(amount))


client.start()
client.run_until_disconnected()
