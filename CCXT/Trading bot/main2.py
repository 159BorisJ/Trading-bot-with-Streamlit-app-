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
symbol3 = "AIXBT/USDC"
symbol4 = "ETH/EUR"

# Nastavenie tak, aby sa vypisovali všetky riadky
pd.set_option('display.max_rows', None)

# Ak chceš vypisovať aj všetky stĺpce
pd.set_option('display.max_columns', None)


def get_data(exchange, symbol, retries=5, delay=2):
    """
    Funkcia na získanie OHLCV dát pre zvolený symbol z Binance a ich konverzia na DataFrame.

    Args:
        symbol (str): Symbol obchodného páru (napr. 'BTC/USDT').
        retries (int): Počet pokusov o získanie dát pri chybe.
        delay (int): Čas (v sekundách) medzi jednotlivými pokusmi.

    Returns:
        pd.DataFrame: DataFrame obsahujúci stĺpce:
                      ['timestamp', 'open', 'high', 'low', 'close', 'volume'].
    """

    timeframe = "5m"  # Časový rámec pre sviečky
    limit = 450  # Počet sviečok na získanie

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


def truncate_to_three_decimals(number, decimal_places):
    # Premena čísla na string
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


def calculate_rsi(data, period=14):
    """
    Funkcia na výpočet RSI (Relative Strength Index) s knižnicou Pandas.

    Args:
        data (pd.DataFrame): DataFrame s cenami, musí obsahovať stĺpec 'close'.
        period (int): Počet období pre výpočet RSI.

    Returns:
        pd.Series: RSI hodnoty.
    """
    # Výpočet rozdielu uzatváracích cien
    delta = data['close'].diff()

    # Oddelenie rastov a poklesov
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    # Výpočet priemerných ziskov a strát
    avg_gain = pd.Series(gain).rolling(window=period, min_periods=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period, min_periods=period).mean()

    # Výpočet RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi.round(2)


def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    """
    Vypočíta MACD (Moving Average Convergence Divergence) a signálnu líniu.

    Parametre:
    - data: DataFrame s cenami, očakáva sa stĺpec 'Close'.
    - short_window: Perióda pre krátkodobý EMA.
    - long_window: Perióda pre dlhodobý EMA.
    - signal_window: Perióda pre signálnu líniu.

    Výstup:
    - DataFrame s pridanými stĺpcami 'MACD' a 'Signal_Line'.
    """
    # Výpočet exponenciálnych kĺzavých priemerov
    short_ema = data['close'].ewm(span=short_window, adjust=False).mean()
    long_ema = data['close'].ewm(span=long_window, adjust=False).mean()

    # Výpočet MACD línie
    data['MACD'] = (short_ema - long_ema).round(2)

    # Výpočet signálnej línie
    data['signal_line'] = data['MACD'].ewm(span=signal_window, adjust=False).mean().round(2)

    return data


def bullish_engulfing_candle(last_closed_candle, prev_closed_candle):
    is_bullish_engulfing = False

    if (prev_closed_candle["close"] < prev_closed_candle["open"] and      # Predchádzajúca sviečka je červená
            last_closed_candle["close"] > last_closed_candle["open"] and  # Posledná sviečka je zelená
            last_closed_candle["open"] < prev_closed_candle["close"] and  # Otvorenie pod zatvorením predchádzajúcej sviečky
            last_closed_candle["close"] > prev_closed_candle["open"]):    # Zatvorenie nad otvorením predchádzajúcej sviečky
        is_bullish_engulfing = True

    return is_bullish_engulfing


def run_strategy_for_account(exchange, strategy, symbol):
    while True:
        try:
            data = get_data(exchange, symbol)
            strategy(data, symbol)
        except Exception as e:
            print(f"Error in strategy execution: {e}")
        time.sleep(60 * 5)  # Spustenie každých 5 minút


# Inicializácia stratégie
# macd_strategy_trailing_instance = MACDStrategyTrailingSL()
sl_tp_macd_strategy_instance = MACDStrategySLTP()
sma_cross_strategy_instance = SMACrossStrategy()

# Spustenie stratégie vo vláknach
thread1 = threading.Thread(target=run_strategy_for_account, args=(
    exchange4,  # Rovnaký podúčet na sťahovanie dát všade
    lambda df, symbol4: sl_tp_macd_strategy_instance.execute(df, symbol4, f"macd_strategy_main - ETH/EUR",
        exchange4, truncate_to_three_decimals, calculate_macd, "EUR", "ETH"),
    symbol4  # Rozličný symbol, o ktorom dáta sťahujeme
))

thread2 = threading.Thread(target=run_strategy_for_account, args=(
    exchange3,  # Rovnaký podúčet na sťahovanie dát všade
    lambda df, symbol: sl_tp_macd_strategy_instance.execute(df, symbol, f"macd_strategy_a3 - BTC/EUR",
        exchange3, truncate_to_three_decimals, calculate_macd, "EUR", "BTC"),
    symbol  # Rozličný symbol, o ktorom dáta sťahujeme
))

# thread3 = threading.Thread(target=run_strategy_for_account, args=(
#     exchange2,
#     lambda df, symbol: sl_tp_macd_strategy_instance.execute(df, symbol, f"macd_strategy - {symbol3}", exchange2, truncate_to_three_decimals, calculate_macd),
#     symbol3
# ))

# Spustenie vlákien paralelne
thread1.start()
thread2.start()
# thread3.start()

# Čaká na dokončenie oboch vlákien
thread1.join()
thread2.join()
# thread3.join()

