import numpy as np
import pandas as pd
import time as tm
from datetime import datetime, time
from bs4 import BeautifulSoup

from Binance import BinanceException, Binance
from secrets import api_id, api_hash #insert here your Binance API keys
from config import users
from utils import *

from telethon import events

import pandas as pd


client = TelegramClient('DCAVG_bot_session', api_id, api_hash).start()


@client.on(events.NewMessage())
async def my_event_handler(event):
    sender = await event.get_sender()
    print(sender.username, str(event.chat_id))

    if 'start' in event.text:
        users = pd.read_csv('./users.csv')
        if sender.username in list(users.telegram_username):
            rows = users[users.telegram_username == sender.username].index
            for row_index in rows:
                users.loc[row_index,'telegram_id'] = event.chat_id
            users.to_csv('./users.csv', index=False)
            await event.respond('Your data has been loaded, you will now receive eventual notifications here!')
        else:
            await event.respond('You are still not registered on DCAVG, please sign up at ///.com')
    #name = utils.get_display_name(sender)
    #print(sender, 'said', event.text, '!')
    #return 
    
    if 'report' in event.text.lower():
        users = pd.read_csv('./users.csv')
        if sender.username in list(users.telegram_username):
            rows = users[users.telegram_username == sender.username]
            user = rows.username.values[0]
            create_excel_file(user)
            await event.respond('Your excel report is coming ;)')
            await client.send_file(event.chat_id, './excel_files/{}.xlsx'.format(user))


client.start()
client.run_until_disconnected()


#send_message_telegram(client, '13218410', 'test')