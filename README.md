
# DCAVG: Bitcoin Daily Dollar Cost Averaging (DCA)
**Tool that allows you to buy Bitcoin automatically every day (or almost every day)**

With this tool you will never forget to buy your daily bitcoins. In fact, everything will be done automatically using the APIs of your Binance or Coinbase account.
The bot will buy daily the correspondent in Bitcoin of an amount in euro defined by the user, through a "MARKET" trade for BTC-EUR.

If the EUR value of the Bitcoins to buy is lower than 10EUR or 0.001BTC, which is the minimum value to trade on Binance and Coinbase, then the bot will postpone the purchase to the next day until the value reaches at least the minimum value.
All the information collected daily is saved on a csv `./src/data.csv`, so you can have the information available for possible analysis for your portfolio.   To manage multiple users, you can also receive an excel report of all transactions made for a specific user, directly on telegram.

The manager of this tool, can set their Telegram keys to  to the `./src/secrets.py` file and configure the purchase settings for each user to `./src/users.csv`.  It is possible to specify for each user, their own telegram username, in this way you can receive reports by sending a message with "/report" to the [@dcavg_bot](http://t.me/dcavg_bot).  

The telegram bot must have been started by running the [DCAVG_telegram_bot.py](https://github.com/jerryfane/DCAVG/blob/master/src/DCAVG_telegram_bot.py).

While the start the DCAVG bot just run `./src/DCAVG.py`. If you don't want to start the bot yourself, you can contact me and I will start it for you. All you need to do is share the API Keys of your exchange account.

---

### I developed this tool out of personal need, I gladly accept external help to develop it further.

## To do

 - ~~Add Telegram message notification system~~
 - Add an automatic USDT recharge system to your account directly from FIAT and/or ERC-20 wallets.
 - ~~Allow you to manage the purchase of Bitcoin for multiple users with centralized funds management~~ *solved with Exchange API*
 - Allows you to manage the purchase of Bitcoin for multiple users with decentralized fund management
