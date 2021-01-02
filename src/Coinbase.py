import cbpro
import pandas as pd
import time as tm

class CoinbasePro():

    def __init__(self, API_KEY, SECRET_KEY, PASSPHRASE):
        self.API_KEY = API_KEY
        self.SECRET_KEY = SECRET_KEY
        self.PASSPHRASE = PASSPHRASE
        self.auth_client = cbpro.AuthenticatedClient(API_KEY, SECRET_KEY, PASSPHRASE)
        self.public_client = cbpro.PublicClient()

    def get_servertime(self):
        return self.public_client.get_time()['epoch']

    def get_price(self, product_id):
        return self.public_client.get_product_ticker(product_id)['price']

    def market_buy_funds(self, order_type, product_id, funds):
        order = self.auth_client.buy(order_type=order_type,
                                        product_id=product_id,
                                        funds=funds)
        return order['id']

    def market_buy_size(self, order_type, product_id, size):
        order = self.auth_client.buy(order_type=order_type,
                                        product_id=product_id,
                                        size=size)
        return order['id']

    def check_order_filled(self, order_id):
        data = self.auth_client.get_order(order_id)
        if data['done_reason'] == 'filled': return True
        else: return False

    def get_filled_order_data(self, order_id):
        return self.auth_client.get_fills(order_id=order_id)

    def buy_BTC(self, order_type, quantity, price=0):
        order_id = self.market_buy_size(order_type.lower(), 'BTC-EUR', quantity)
        tm.sleep(5)
        if self.check_order_filled(order_id):
            return self.get_filled_order_data(order_id)
        
