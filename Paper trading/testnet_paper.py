import sys
import time

# Cesta k virtuálnemu prostrediu
venv_path = r"C:\Users\admin\Desktop\Trading app\venv\Lib\site-packages"
sys.path.append(venv_path)

from binance.client import Client
from binance.enums import *

# Tvoje API kľúče z testnetu
api_key = "pkwbjErGStfrgTVRv2fW1c18FliTrFzogPThrayufz2X9mEft02a6QEsqDVQYl7P"
api_secret = "lETefNqNzyMyUTNS4Gd5tZ5ENl6Mc5XD7o9dNJWF7BOA8ssGnPms6REHr48Caako"

client = Client(api_key, api_secret, testnet=True)
client.API_URL = 'https://testnet.binance.vision/api'

# Parametre stratégie
SYMBOL = 'BTCUSDT'  # Mena na obchodovanie
BUY_THRESHOLD = 100_000  # Nákupná hranica (napr. 100 000 USDT)
SELL_THRESHOLD = 105_000  # Predajná hranica (napr. 105 000 USDT)
TRADE_QUANTITY = 0.001  # Množstvo BTC na obchodovanie


def check_and_trade():
    # Získaj aktuálnu trhovú cenu
    ticker = client.get_symbol_ticker(symbol=SYMBOL)
    current_price = float(ticker['price'])
    print(f"Aktuálna cena {SYMBOL}: {current_price} USDT")

    # Skontroluj aktuálny stav na účte
    balances = client.get_account()['balances']
    btc_balance = next((item for item in balances if item['asset'] == 'BTC'), None)
    usdt_balance = next((item for item in balances if item['asset'] == 'USDT'), None)
    btc_free = float(btc_balance['free']) if btc_balance else 0.0
    usdt_free = float(usdt_balance['free']) if usdt_balance else 0.0

    print(f"BTC k dispozícii: {btc_free}, USDT k dispozícii: {usdt_free}")

    # Podmienka na nákup
    if current_price < BUY_THRESHOLD and usdt_free >= current_price * TRADE_QUANTITY:
        print("Cena klesla pod hranicu. Nákup BTC...")
        order = client.order_market_buy(
            symbol=SYMBOL,
            quantity=TRADE_QUANTITY
        )
        print(f"Nákupná objednávka: {order}")

    # Podmienka na predaj
    elif current_price > SELL_THRESHOLD and btc_free >= TRADE_QUANTITY:
        print("Cena stúpla nad hranicu. Predaj BTC...")
        order = client.order_market_sell(
            symbol=SYMBOL,
            quantity=TRADE_QUANTITY
        )
        print(f"Predajná objednávka: {order}")
    else:
        print("Žiadna akcia - podmienky nesplnené.")


# Spustenie stratégie
print("Začiatok stratégie...")
while True:
    try:
        check_and_trade()
        time.sleep(60)  # Spustenie každú minútu
    except Exception as e:
        print(f"Chyba: {e}")
        break





