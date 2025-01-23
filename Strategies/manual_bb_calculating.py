import ccxt
import config
import pandas as pd
import threading
import time
import json


exchange = ccxt.binance({
    "apiKey": config.API_KEY,
    "secret": config.API_SECRET,
    'enableRateLimit': True,
    "timeout": 30000,
})

# define the trading parameters
symbols = ["BTC/EUR", "ETH/EUR", "BNB/EUR"]

lock = threading.Lock()


# Funkcia na načítanie trhových dát
def get_data(symbol):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe="1d", limit=40)
    with lock:
        # print()
        # print(f"Data for crypto {symbol}")
        # print()
        data = []
        for candle in ohlcv:
            timestamp = pd.to_datetime(candle[0], unit="ms")
            open_price = candle[1]
            high_price = candle[2]
            low_price = candle[3]
            close_price = candle[4]
            volume = candle[5]
            data.append([timestamp, open_price, high_price, low_price, close_price, volume])

        # df = pd.DataFrame(data, columns=["datetime", "open", "high", "low", "close", "volume"])
        # df.set_index("datetime", inplace=True)
        # data_feed = CustomPandasData(dataname=df)

        return data


def get_prices(data):
    prices_dict = {}
    for crypto in data:
        price = [float(candle["open"]) for candle in data[crypto]]
        prices_dict[crypto] = price
    return prices_dict


def calculate_sma(data, days):
    sma_dict = {}
    for crypto, prices in data.items():  # Pre každú kryptomenu v dátach
        sma_values = []
        for i in range(len(prices) - days + 1):  # Iteruje cez všetky možné SMA hodnoty
            sma = sum(prices[i:i + days]) / days  # Počíta SMA pre dané obdobie
            sma_values.append(sma)  # Ukladá SMA do zoznamu
        sma_dict[crypto] = sma_values  # Priradí zoznam SMA k danej kryptomene
    return sma_dict


def calculate_standard_deviation():
    pass


while True:
    market_data_prettier = {}
    market_data = {}

    for symbol in symbols:
        data = get_data(symbol)

        # Prevod dát na serializovateľný formát
        serializable_data = []
        for row in data:
            serializable_row = {
                "datetime": row[0].strftime('%Y-%m-%d %H:%M:%S'),  # Konverzia Timestamp na string
                "open": row[1],
                "high": row[2],
                "low": row[3],
                "close": row[4],
                "volume": row[5],
            }
            serializable_data.append(serializable_row)

            market_data_prettier[symbol] = serializable_data  # Prehľadné dáta na testovací výpis
            market_data[symbol] = data  # Dáta na použitie v backtraderi

    # print(json.dumps(market_data_prettier, indent=4))  # Výpis prehľadných dát
    # print(market_data)  # Výpis dát pre backtrader

    # print(json.dumps(get_prices(market_data_prettier), indent=4))

    prices_dict = get_prices(market_data_prettier)

    print(json.dumps(calculate_sma(prices_dict, 20)))

    time.sleep(86400)




