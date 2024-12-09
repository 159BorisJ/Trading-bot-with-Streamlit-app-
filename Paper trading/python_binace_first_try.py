import sys
import pandas
import json
import requests
import pandas as pd
import datetime
import websocket

# Cesta k virtuálnemu prostrediu
venv_path = r"C:\Users\admin\Desktop\Trading app\venv\Lib\site-packages"
sys.path.append(venv_path)

from binance import Client
from dotenv import load_dotenv

load_dotenv()

API_KEY = 'fNeobg28tAVaSTZtgCyVopoSvLC0cZZrOZP16sqOyCoez1Ux35JKUyTgF3ncTmL3'
API_SECRET = 'JeC4ue9z00cPbpDkrAhC9hvT0cvk2oEiFeXmD0xq3s9cU4YODcJA7O3pgMTaY7lr'

# Inicializácia klienta
client = Client(API_KEY, API_SECRET, testnet=True)

# tickers = client.get_all_tickers()

url = "https://api1.binance.com"
api_call = "/api/v3/ticker/price"
headers = {"content-type": "application/json", "X-MBX-APIKEY": API_KEY}
response = requests.get(url + api_call, headers=headers)
response = json.loads(response.text)
# print(response)

# # df = pd.DataFrame.from_records(response)
# # print(df.head())
#
# # print(client.ping())
#
# res = client.get_server_time()
# # print(res)
#
# ts = res["serverTime"] / 1000
# your_dt = datetime.datetime.fromtimestamp(ts)
# your_dt.strftime("%Y-%m-%d %H:%H:%S")
# # print(your_dt)
#
# # coin_info = client.get_all_tickers()
# # df = pd.DataFrame(coin_info)
# # print(df.head())
#
# exchange_info = client.get_exchange_info()
# # print(exchange_info.keys())
#
# symbol_info = client.get_symbol_info("BTCUSDT")
# # print(symbol_info)
#
# # df = pd.DataFrame(exchange_info["symbols"])
# # print(df)
#
# market_depth = client.get_order_book(symbol="BTCUSDT")
# # print(market_depth)
# bids = pd.DataFrame(market_depth["bids"])
# bids.columns = ["price", "bids"]
# asks = pd.DataFrame(market_depth["asks"])
# asks.columns = ["price", "asks"]
# # df = pd.concat([bids, asks]).fillna(0)
# # print(df)
#
# recent_trades = client.get_recent_trades(symbol="BTCUSDT")
# df = pd.DataFrame(recent_trades)
# # print(df)
#
# id = df.loc[450, "id"]
# historical_trades = client.get_historical_trades(symbol="BTCUSDT", limit=1000, fromId=id)
# # df = pd.DataFrame(historical_trades)
# # print(df)
#
# avg_price = client.get_avg_price(symbol="BTCUSDT")
# # print(avg_price)
#
# tickers = client.get_ticker()
# df = pd.DataFrame(tickers)
# print(df)
#
#
# ### Account Endpoints ###
#
# # Get Binance Account Info
# info = client.get_account()
# print(info)
#
# # Get Binance Asset Details
# asset_balance = client.get_asset_balance(asset="ETH")
# print(asset_balance)
#
# # Get Binance Trades
# trades = client.get_my_trades(symbol="BTCUSDT")
# print()
# print(trades)
#
# # Fetch All Binance Orders
# orders = client.get_all_orders(symbol="BTCUSDT")
# print()
# print(orders)
#
# coin_info = client.get_all_tickers()
# df = pd.DataFrame(coin_info)
# df = df[df["symbol"] == "BTCUSDT"]
# df["price"] = df["price"].astype(float)
# price = df["price"].values[0]
# print(price * 0.0005)
#
# # Place Binance Order
# buy_order = client.create_test_order(symbol="BTCUSDT",
#                                      side="buy",
#                                      type="MARKET",
#                                      quantity=0.0005)
# print(buy_order)
#
# order_status = client.order_market_buy(symbol="BTCUSDT", quantity=0.0005)
# print(order_status)
#
# # Chceck Binance Order Status
# order_response = client.get_order(symbol="BTCUSDT", orderId=order_status["orderId"])
# print()
# print(order_response)
#
# # Cancel Binance Order
# # order = client.cancel_order(symbol="BTCUSDT", orderId="your_order_id")


### Binance WebSockets ###

# symbol = "btcusdt"
# socket = f"wss://stream.binance.com:9443/ws/{symbol}@trade"
#
#
# df = pd.DataFrame()
#
#
# def on_message(ws, message):
#     msg = json.loads(message)
#     d = [(msg["T"], msg["p"])]
#     global df
#     df = pd.concat([df, pd.DataFrame.from_records(d)])
#
#
# def on_error(ws, error):
#     print(error)
#
#
# def on_close(ws, close_status_code, close_msg):
#     print("### closed ###")
#     df.columns = ["time", "price"]
#     df["time"] = pd.to_datetime(df["time"], unit="ms")
#     df.set_index(df["time"], inplace=True)
#     df.drop(columns="time", inplace=True)
#     print(df)
#
#
# def on_open(ws):
#     print("Opened connection")
#
#
# ws = websocket.WebSocketApp(socket,
#                             on_open=on_open,
#                             on_message=on_message,
#                             on_error=on_error,
#                             on_close=on_close)
#
# ws.run_forever()

symbol = "btcusdt"
socket = f"wss://stream.binance.com:9443/ws/{symbol}@kline_1m"


df = pd.DataFrame()


# def on_message(ws, message):
#     print(message)
#
#
# def on_error(ws, error):
#     print(error)
#
#
# def on_close(ws, close_status_code, close_msg):
#     print("### closed ###")
#
#
# def on_open(ws):
#     print("Opened connection")
#
#
# ws = websocket.WebSocketApp(socket,
#                             on_open=on_open,
#                             on_message=on_message,
#                             on_error=on_error,
#                             on_close=on_close)
#
# ws.run_forever()

t, o, h, l, c, v = [], [], [], [], [], []


def on_message(ws, message):
    msg = json.loads(message)
    bar = msg["k"]
    if bar["x"] == False:
        t.append(bar["t"])
        o.append(bar["o"])
        h.append(bar["h"])
        l.append(bar["l"])
        c.append(bar["c"])
        v.append(bar["v"])


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("### closed ###")
    bars = {"time": t, "open": o, "high": h, "low": l, "close": c, "volume": v}
    df = pd.DataFrame.from_dict(bars)
    df.set_index("time", inplace=True)
    print(df)


def on_open(ws):
    print("Opened connection")


ws = websocket.WebSocketApp(socket,
                            on_open=on_open,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)

ws.run_forever()


# Načítanie aktuálnych cien kryptomien
# try:
#     prices = client.get_all_tickers()
#     print("Aktuálne ceny kryptomien:")
#     for price in prices[:10]:  # Výpis len prvých 10 mien
#         print(f"{price['symbol']}: {price['price']}")
#
# except Exception as e:
#     print("Chyba pri načítaní dát:", e)



