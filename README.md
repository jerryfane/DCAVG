
# DCAVG: Cryptocurrency Daily Dollar Cost Averaging (DCA)
**Tool that allows you to buy ANY CRYPTOCURRENCY automatically every day (or almost every day)**

With this tool you will never forget to buy your daily cryptocurrencies. Indeed, you can use it to buy any cryptocurrency automatically through the API of various exchanges, at the moment Binance and Coinbase Pro. The tool buys a predefined amount of crypto through a "MARKET" trade for CRYPTO_NAME-EUR.

If the EURO value of the crypto to buy is less than 10EURO, which is the minimum amount required to trade on Binance and Coinbase, then it postpones the purchase for the following days. It will save the amount it would have bought until it reaches at least this minimum required amount.

All the information saved daily, are stored on `./src/datasets/data.csv`.

Who will deploy this tool, will be able to easily manage multiple users, and configure their settings on `./src/datasets/users.csv`, moreover he will need to insert his Pushover API key to the `./src/config.py` file. In this way users will be able to receive a notification whenever the bot manage to buy cryptos.

To start the DCAVG bot just run `./src/main.py`.

---

### Updates

#### March 7, 2021

A new feature has been introduced that allows users to increase the amount of BTC to buy automatically, if the price of Bitcoin has decreased from the day before. This feature is configurable for each user in the file `./src/datasets/users.csv`.

Basically if the user wants to buy 1 euro of Bitcoin per day, and the price of BTC has decreased by 10% compared to the previous day, then he will buy 1.1 euro.

---

### I developed this tool out of personal need, I gladly accept external help to develop it further.

## To do

 - ~~Add Telegram message notification system (Deprecated)~~
 - ~~Add Pushover message notification system~~
 - Add an automatic USDT recharge system to your account directly from FIAT and/or ERC-20 wallets.
 - ~~Allow you to manage the purchase of Bitcoin for multiple users with centralized funds management~~ *solved with Exchange API*
 - Allows you to manage the purchase of Bitcoin for multiple users with decentralized fund management
