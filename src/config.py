import pandas as pd

users = {}
users_df = pd.read_csv('./users.csv')

for user in users_df['username']:
    users[user] = {}
    users[user]['buy_eur_per_day'] = users_df[users_df['username'] == user]['buy_eur_per_day'].values[0]
    #set true if you want to get the amount of BTC to buy from the amount saved on data.csv
    users[user]['continue_from_last_day'] = users_df[users_df['username'] == user]['continue_from_last_day'].values[0]
    users[user]['btc_to_buy'] = users_df[users_df['username'] == user]['btc_to_buy'].values[0]
    users[user]['API_KEY'] = users_df[users_df['username'] == user]['API_KEY'].values[0]
    users[user]['SECRET_KEY'] = users_df[users_df['username'] == user]['SECRET_KEY'].values[0]
    users[user]['telegram_username'] = users_df[users_df['username'] == user]['telegram_username'].values[0]
    users[user]['telegram_id'] = users_df[users_df['username'] == user]['telegram_id'].values[0]


for user in users:
    if users[user]['continue_from_last_day'] == True:
        data = pd.read_csv('./data.csv')
        btc_to_buy = data[data['user'] == user]['total_btc'].values[-1]
        users[user]['btc_to_buy'] = btc_to_buy
