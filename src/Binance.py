import json
import hmac
import hashlib
import requests
from urllib.parse import urljoin, urlencode
import time


class BinanceException(Exception):
    def __init__(self, status_code, data):

        self.status_code = status_code
        if data:
            self.code = data['code']
            self.msg = data['msg']
        else:
            self.code = None
            self.msg = None
        message = f"{status_code} [{self.code}] {self.msg}"

        # Python 2.x
        # super(BinanceException, self).__init__(message)
        super().__init__(message)

class Binance():
    def __init__(self, API_KEY, SECRET_KEY):
        self.API_KEY = API_KEY
        self.SECRET_KEY = SECRET_KEY
        self.BASE_URL = 'https://api.binance.com'

        self.headers = {
            'X-MBX-APIKEY': API_KEY
        }

    def get_servertime(self):
        PATH =  '/api/v1/time'
        params = None

        timestamp = int(time.time() * 1000)

        url = urljoin(self.BASE_URL, PATH)
        r = requests.get(url, params=params)
        if r.status_code == 200:
            #print(json.dumps(r.json(), indent=2))
            data = r.json()
            return data['serverTime']
            #print(f"diff={timestamp - data['serverTime']}ms")
        else:
            raise BinanceException(status_code=r.status_code, data=r.json())

    def get_price(self, symbol):
        PATH = '/api/v3/ticker/price'
        params = {
            'symbol': symbol
        }

        url = urljoin(self.BASE_URL, PATH)
        r = requests.get(url, headers=self.headers, params=params)
        if r.status_code == 200:
            return r.json()
        else:
            raise BinanceException(status_code=r.status_code, data=r.json())

    def get_binance_orderbook(self, symbol, limit=5):
        PATH = '/api/v1/depth'
        params = {
            'symbol': symbol,
            'limit': limit
        }

        url = urljoin(self.BASE_URL, PATH)
        r = requests.get(url, headers=self.headers, params=params)
        if r.status_code == 200:
            return r.json()
        else:
            raise BinanceException(status_code=r.status_code, data=r.json())


    def create_binance_order(self, symbol, side, Type, quantity, price=0):
        PATH = '/api/v3/order'
        timestamp = int(time.time() * 1000)

        params = {
            'symbol': symbol,
            'side': side,
            'type': Type,
            'timeInForce': 'GTC',
            'quantity': quantity,
            'price': price,
            'recvWindow': 5000,
            'timestamp': timestamp,
        }

        if Type == 'MARKET':
            params.pop('price')
            params.pop('timeInForce')

        query_string = urlencode(params)
        params['signature'] = hmac.new(self.SECRET_KEY.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

        url = urljoin(self.BASE_URL, PATH)
        r = requests.post(url, headers=self.headers, params=params)
        if r.status_code == 200:
            data = r.json()
            return data
        else:
            raise BinanceException(status_code=r.status_code, data=r.json())

    def buy_crypto(self, Type, quantity, symbol, price = 0):
        side = 'BUY'

        if Type == 'MARKET': order_data = self.create_binance_order(symbol, side, Type, quantity)
        elif Type == 'LIMIT': order_data = self.create_binance_order(symbol, side, Type, quantity, price)
        else: return "can't recognize type order"
        return order_data
