import sys
import time
import json

# Cesta k virtuálnemu prostrediu
venv_path = r"C:\Users\admin\Desktop\Trading app\venv\Lib\site-packages"
sys.path.append(venv_path)

from binance.client import Client
from binance.enums import *

# Tvoje API kľúče z testnetu
api_key = "pkwbjErGStfrgTVRv2fW1c18FliTrFzogPThrayufz2X9mEft02a6QEsqDVQYl7P"
api_secret = "lETefNqNzyMyUTNS4Gd5tZ5ENl6Mc5XD7o9dNJWF7BOA8ssGnPms6REHr48Caako"

client = Client(api_key, api_secret, testnet=True)

account = client.get_account()
print(json.dumps(account, indent=4))

symbol = "BTCUSDT"
buy_price_threshold = 60
sell_price_threshold = 68000
trade_quantity = 0.001


def get_current_price(symbol):
    ticker = client.get_symbol_ticker(symbol=symbol)
    return float(ticker["price"])


def get_average_price(symbol):
    # Získanie údajov o trhu za posledných 24 hodín
    ticker = client.get_ticker(symbol=symbol)
    high_price = ticker["high"]
    low_price = ticker["low"]
    print(f"High price: {high_price}")
    print(f"Low price: {low_price}")


def place_buy_order(symbol, quantity):
    order = client.order_market_buy(symbol=symbol, quantity=quantity)
    print(f"Buy order done: {order}")


def place_sell_order(symbol, quantity):
    order = client.order_market_sell(symbol=symbol, quantity=quantity)
    print(f"Sell order done: {order}")


def trading_bot():
    in_position = False

    while True:
        current_price = get_current_price(symbol)
        print(f"Current price of {symbol}: {current_price}")

        if not in_position:
            if current_price < buy_price_threshold:
                print(f"Price is below {buy_price_threshold}. Placing buy order.")
                place_buy_order(symbol, trade_quantity)
                in_position = True
        else:
            if current_price > sell_price_threshold:
                print(f"Price is above {sell_price_threshold}. Placing sell order.")
                place_sell_order(symbol, trade_quantity)
                in_position = False

        time.sleep(5)


get_average_price(symbol)


