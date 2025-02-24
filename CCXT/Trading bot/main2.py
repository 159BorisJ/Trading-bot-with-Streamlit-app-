import ccxt
import pandas as pd
import config2
import time
import pytz
import threading
import backtrader as bt
import numpy as np

# from trailing_macd_strategy import MACDStrategyTrailingSL
from sl_tp_macd_strategy import MACDStrategySLTP
from sma_cross_strategy import SMACrossStrategy
from scavenger import ScavengerStrategy
from trailing_sl_macd_strategy import TrailingSLMACDStrategy

exchange_a1 = ccxt.binance({
    "apiKey": config2.SUB_A1_API_KEY,
    "secret": config2.SUB_A1_SECRET_KEY,
    'enableRateLimit': True,
    "timeout": 30000,
})

exchange_a2 = ccxt.binance({
    "apiKey": config2.SUB_A2_API_KEY,
    "secret": config2.SUB_A2_SECRET_KEY,
    'enableRateLimit': True,
    "timeout": 30000,
})

exchange_a3 = ccxt.binance({
    "apiKey": config2.SUB_A3_API_KEY,
    "secret": config2.SUB_A3_API_SECRET,
    'enableRateLimit': True,
    "timeout": 30000,
})

exchange_main = ccxt.binance({
    "apiKey": config2.MAIN_API_KEY,
    "secret": config2.MAIN_API_SECRET,
    'enableRateLimit': True,
    "timeout": 30000,
})

symbol = "BTC/EUR"
symbol2 = "ETH/EUR"
symbol3 = "BNB/EUR"
symbol4 = "ADA/EUR"

# Nastavenie tak, aby sa vypisovali všetky riadky
pd.set_option('display.max_rows', None)

# Ak chceš vypisovať aj všetky stĺpce
pd.set_option('display.max_columns', None)


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


def truncate_to_three_decimals(number, decimal_places):  # Premenovať túto funkciu
    num_str = str(number)
    # Nájdeme pozíciu desatinnej bodky
    decimal_index = num_str.find('.')
    if decimal_index == -1:
        # Ak desatinná bodka neexistuje, vrátime pôvodné číslo
        return number
    # Upravíme string tak, že ponecháme 3 znaky za bodkou
    truncated_str = num_str[:decimal_index + decimal_places + 1]  # +4 zahŕňa bodku a 3 desatinné miesta
    # Premena späť na číslo
    return float(truncated_str)


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


def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    # Výpočet exponenciálnych kĺzavých priemerov
    short_ema = data['close'].ewm(span=short_window, adjust=False).mean()
    long_ema = data['close'].ewm(span=long_window, adjust=False).mean()

    # Výpočet MACD línie
    data['MACD'] = (short_ema - long_ema).round(2)

    # Výpočet signálnej línie
    data['signal_line'] = data['MACD'].ewm(span=signal_window, adjust=False).mean().round(2)

    return data


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


def run_strategy_for_account(exchange, strategy, symbol, timeframe, limit):
    while True:
        try:
            data = get_data(exchange, symbol, timeframe, limit)
            strategy(data, symbol)
        except Exception as e:
            print(f"Error in strategy execution: {e}")
        time.sleep(60 * 2.5)


# Inicializácia stratégií
sl_tp_macd_strategy_instance_main = MACDStrategySLTP(6)
sl_tp_macd_strategy_instance_a1 = MACDStrategySLTP(5)
sl_tp_macd_strategy_instance_a2 = MACDStrategySLTP(3)
sl_tp_macd_strategy_instance_a3 = MACDStrategySLTP(3)

trailing_macd_instance_main = TrailingSLMACDStrategy(6)
trailing_macd_instance_a1 = TrailingSLMACDStrategy(5)
trailing_macd_instance_a2 = TrailingSLMACDStrategy(3)
trailing_macd_instance_a3 = TrailingSLMACDStrategy(3)

# Spustenie stratégie vo vláknach
thread1 = threading.Thread(target=run_strategy_for_account, args=(
    exchange_main,
    lambda df, symbol: trailing_macd_instance_main.execute(
        df,
        symbol,
        f"trailing_macd_strategy - BTC/EUR",
        exchange_main,
        truncate_to_three_decimals,
        calculate_macd,
        "EUR",
        "BTC"),
    symbol, "15m", 480
))

thread2 = threading.Thread(target=run_strategy_for_account, args=(
    exchange_a1,
    lambda df, symbol2: trailing_macd_instance_a1.execute(
        df,
        symbol2,
        f"trailing_macd_strategy - ETH/EUR",
        exchange_a1,
        truncate_to_three_decimals,
        calculate_macd,
        "EUR",
        "ETH"),
    symbol2, "15m", 480
))

thread3 = threading.Thread(target=run_strategy_for_account, args=(
    exchange_a2,
    lambda df, symbol3: sl_tp_macd_strategy_instance_a2.execute(
        df,
        symbol3,
        f"sl_tp_macd_strategy - BNB/EUR",
        exchange_a2,
        truncate_to_three_decimals,
        calculate_macd,
        "EUR",
        "BNB"),
    symbol3, "15m", 480
))

thread4 = threading.Thread(target=run_strategy_for_account, args=(
    exchange_a3,
    lambda df, symbol4: sl_tp_macd_strategy_instance_a3.execute(
        df,
        symbol4,
        f"sl_tp_macd_strategy - ADA/EUR",
        exchange_a3,
        truncate_to_three_decimals,
        calculate_macd,
        "EUR",
        "ADA"),
    symbol4, "15m", 480
))

# Spustenie vlákien paralelne
thread1.start()
thread2.start()
thread3.start()
thread4.start()

# Čakanie na dokončenie vlákien
thread1.join()
thread2.join()
thread3.join()
thread4.join()

