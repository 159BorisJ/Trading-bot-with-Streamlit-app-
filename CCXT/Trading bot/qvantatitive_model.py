import ccxt
import pandas as pd
import config2
import time
import pytz
import threading
import backtrader as bt
import numpy as np
import json

# from trailing_macd_strategy import MACDStrategyTrailingSL
from sl_tp_macd_strategy import MACDStrategySLTP
from sma_cross_strategy import SMACrossStrategy
from scavenger import ScavengerStrategy

exchange1 = ccxt.binance({
    "apiKey": config2.SUB_BB_API_KEY,
    "secret": config2.SUB_BB_API_SECRET,
    'enableRateLimit': True,
    "timeout": 30000,
})

exchange2 = ccxt.binance({
    "apiKey": config2.SUB_EMA_API_KEY,
    "secret": config2.SUB_EMA_API_SECRET,
    'enableRateLimit': True,
    "timeout": 30000,
})

exchange3 = ccxt.binance({
    "apiKey": config2.SUB_A3_API_KEY,
    "secret": config2.SUB_A3_API_SECRET,
    'enableRateLimit': True,
    "timeout": 30000,
})

exchange4 = ccxt.binance({
    "apiKey": config2.MAIN_API_KEY,
    "secret": config2.MAIN_API_SECRET,
    'enableRateLimit': True,
    "timeout": 30000,
})

symbol = "BTC/EUR"
symbol2 = "BCH/EUR"
# symbol3 = "AIXBT/USDC"
symbol4 = "ETH/EUR"

symbols = ["BTC/EUR", "BCH/EUR", "ETH/EUR"]

# Nastavenie tak, aby sa vypisovali všetky riadky
pd.set_option('display.max_rows', None)

# Ak chceš vypisovať aj všetky stĺpce
pd.set_option('display.max_columns', None)

data_dict = {}


def get_data(exchange, symbol, timeframe, limit, retries=5, delay=2):

    for attempt in range(retries):
        try:
            # Pokus o získanie dát z Binance
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

            # Konverzia na DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

            # Odstránenie poslednej (nedokončenej) sviečky
            df = df.iloc[:-1]

            # Konverzia 'timestamp' na datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

            # Konverzia na miestny čas
            local_timezone = pytz.timezone("Europe/Bratislava")
            df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert(local_timezone)

            return df  # Úspešne získaný a spracovaný DataFrame sa vráti

        except ccxt.NetworkError as e:
            print(f"NetworkError: {e}. Retrying in {delay} seconds... (attempt {attempt + 1}/{retries})")
            time.sleep(delay)
        except ccxt.ExchangeError as e:
            print(f"ExchangeError: {e}. Stopping retries.")
            break
        except Exception as e:
            print(f"Unhandled error: {e}. Stopping retries.")
            break

    # Ak všetky pokusy zlyhajú, vyhodí sa výnimka
    raise Exception(f"Failed to fetch data for symbol after {retries} retries.")


# Ulož dáta do slovníka
for s in symbols:
    df = get_data(exchange4, s, "15m", 500)
    data_dict[s] = []

    # Iterácia cez riadky DataFrame
    for index, row in df.iterrows():
        timestamp = str(row["timestamp"])
        close = row["close"]

        data_dict[s].append({"timestamp": timestamp, "close": close})

print(json.dumps(data_dict, indent=4))

# Prechádzaj



# def truncate_to_three_decimals(number, decimal_places):
#     # Premena čísla na string
#     num_str = str(number)
#     # Nájdeme pozíciu desatinnej bodky
#     decimal_index = num_str.find('.')
#     if decimal_index == -1:
#         # Ak desatinná bodka neexistuje, vrátime pôvodné číslo
#         return number
#     # Upravíme string tak, že ponecháme 3 znaky za bodkou
#     truncated_str = num_str[:decimal_index + decimal_places + 1]  # +4 zahŕňa bodku a 3 desatinné miesta
#     # Premena späť na číslo
#     return float(truncated_str)
#
#
# def calculate_rsi(data, period=14):
#     # Výpočet rozdielu uzatváracích cien
#     delta = data['close'].diff()
#
#     # Oddelenie rastov a poklesov
#     gain = np.where(delta > 0, delta, 0)
#     loss = np.where(delta < 0, -delta, 0)
#
#     # Výpočet priemerných ziskov a strát
#     avg_gain = pd.Series(gain).rolling(window=period, min_periods=period).mean()
#     avg_loss = pd.Series(loss).rolling(window=period, min_periods=period).mean()
#
#     # Výpočet RSI
#     rs = avg_gain / avg_loss
#     rsi = 100 - (100 / (1 + rs))
#
#     return rsi.round(2)
#
#
# def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
#     # Výpočet exponenciálnych kĺzavých priemerov
#     short_ema = data['close'].ewm(span=short_window, adjust=False).mean()
#     long_ema = data['close'].ewm(span=long_window, adjust=False).mean()
#
#     # Výpočet MACD línie
#     data['MACD'] = (short_ema - long_ema).round(2)
#
#     # Výpočet signálnej línie
#     data['signal_line'] = data['MACD'].ewm(span=signal_window, adjust=False).mean().round(2)
#
#     return data
#
#
# def bullish_engulfing_candle(last_closed_candle, prev_closed_candle):
#     is_bullish_engulfing = False
#
#     if (prev_closed_candle["close"] < prev_closed_candle["open"] and      # Predchádzajúca sviečka je červená
#             last_closed_candle["close"] > last_closed_candle["open"] and  # Posledná sviečka je zelená
#             last_closed_candle["open"] < prev_closed_candle["close"] and  # Otvorenie pod zatvorením predchádzajúcej sviečky
#             last_closed_candle["close"] > prev_closed_candle["open"]):    # Zatvorenie nad otvorením predchádzajúcej sviečky
#         is_bullish_engulfing = True
#
#     return is_bullish_engulfing
#
#
# def run_strategy_for_account(exchange, strategy, symbol, timeframe, limit):
#     while True:
#         try:
#             data = get_data(exchange, symbol, timeframe, limit)
#             strategy(data, symbol)
#         except Exception as e:
#             print(f"Error in strategy execution: {e}")
#         time.sleep(60 * 2.5)  # Spustenie každú minútu * 2.5 kvôli rýchlejším reakciám na zmeny
#
#
# # Inicializácia stratégií
# # macd_strategy_trailing_instance = MACDStrategyTrailingSL()
# sl_tp_macd_strategy_instance_main = MACDStrategySLTP()
# sl_tp_macd_strategy_instance_a3 = MACDStrategySLTP()
# sma_cross_strategy_instance = SMACrossStrategy()
# scavenger_instance = ScavengerStrategy()
#
# # Spustenie stratégie vo vláknach
# thread1 = threading.Thread(target=run_strategy_for_account, args=(
#     exchange4,
#     lambda df, symbol4: sl_tp_macd_strategy_instance_main.execute(
#         df,
#         symbol4,
#         f"macd_strategy_main - ETH/EUR",
#         exchange4,
#         truncate_to_three_decimals,
#         calculate_macd,
#         "EUR",
#         "ETH"),
#     symbol4, "5m", 450
# ))
#
# thread2 = threading.Thread(target=run_strategy_for_account, args=(
#     exchange3,
#     lambda df, symbol4: scavenger_instance.execute(
#         df,
#         symbol4,
#         f"scavenger_strategy - ETH/EUR",
#         exchange3,
#         truncate_to_three_decimals,
#         calculate_macd,
#         "EUR",
#         "ETH"),
#     symbol4, "15m", 500
# ))
#
# # Spustenie vlákien paralelne
# thread1.start()
# thread2.start()
#
# # Čaká na dokončenie oboch vlákien
# thread1.join()
# thread2.join()

