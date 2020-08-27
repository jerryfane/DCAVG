# DCAVG: Binance/Bitcoin Daily Dollar Cost Averaging (DCA)
**Tool that allows you to buy Bitcoin with your Binance account automatically every day (or almost every day)**

With this tool you will never forget to buy your daily bitcoins. In fact, everything will be done automatically using the Binance API of your account. 
The bot will buy daily the correspondent in Bitcoin of an amount in euro defined by the user, through a "MARKET" trade for BTCUSDT. 

If the USD value of the Bitcoins to buy is lower than 10USD, which is the minimum value to trade on Binance, then the bot will postpone the purchase to the next day until the value reaches at least 10USD. 
All the information collected daily is saved on a csv `./src/data.csv`, so you can have the information available for possible analysis for your portfolio.   

You can set this tool by simply adding your Binance API key to the `./src/secrets.py` file and configure the purchase settings to `./src/config.py`. Then run `./src/DCAVG.py`. If you need help, do not hesitate to contact me. 

---

### I developed this tool out of personal need, I gladly accept external help to develop it further.

---

### Update #1 - 08/28/2020

I have improved the program so that it can manage the API keys of multiple accounts, saving all the data in the same CSV with a new "user" column. To add a new user just create a new row in the file `users.csv`, with the configuration and API Keys of the user in question. Then the program will buy Bitcoin following the settings configured for each user. 

---


## To do

 - Add Telegram message notification system to alert you when your USDT balance on your account at Binance is about to run out
 - Add an automatic USDT recharge system to your account directly from FIAT and/or ERC-20 wallets. 
 - Allow you to manage the purchase of Bitcoin for multiple users with centralized funds management
 - Allows you to manage the purchase of Bitcoin for multiple users with decentralized fund management
