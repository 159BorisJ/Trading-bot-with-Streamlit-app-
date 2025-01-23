import ccxt
import pandas as pd
import config
import time
import pytz
import threading
import math

exchange1 = ccxt.binance({
    "apiKey": config.SUB_EMA_API_KEY,
    "secret": config.SUB_EMA_API_SECRET,
    'enableRateLimit': True,
    "timeout": 30000,
})

exchange2 = ccxt.binance({
    "apiKey": config.SUB_BB_API_KEY,
    "secret": config.SUB_BB_API_SECRET,
    'enableRateLimit': True,
    "timeout": 30000,
})

symbol = "LTC/EUR"


def get_data(symbol, retries=5, delay=2):
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
    # exchange = ccxt.binance({
    #     'timeout': 30000,  # Timeout pre požiadavku (30 sekúnd)
    #     'rateLimit': 1200,  # Dodržiavanie limitov Binance API
    # })

    timeframe = "1m"  # Časový rámec pre sviečky
    limit = 50  # Počet sviečok na získanie

    for attempt in range(retries):
        try:
            # Pokus o získanie dát z Binance
            ohlcv = exchange2.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)  # Môžme použiť exchange1 pretože...
            # ...budem obchodovať s tou istou kryptomenou

            # Konverzia na DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

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
    raise Exception(f"Failed to fetch data for {symbol} after {retries} retries.")


def truncate_to_three_decimals(number):
    # Premena čísla na string
    num_str = str(number)
    # Nájdeme pozíciu desatinnej bodky
    decimal_index = num_str.find('.')
    if decimal_index == -1:
        # Ak desatinná bodka neexistuje, vrátime pôvodné číslo
        return number
    # Upravíme string tak, že ponecháme 3 znaky za bodkou
    truncated_str = num_str[:decimal_index + 4]  # +4 zahŕňa bodku a 3 desatinné miesta
    # Premena späť na číslo
    return float(truncated_str)


data = get_data(symbol)

last_row = data.iloc[-1]

market_info = exchange2.fetch_markets()
symbol_info = next((m for m in market_info if m['symbol'] == symbol), None)

sub_account_money_balance = exchange2.fetch_balance()['total']['EUR']

# Získajte informácie o presnosti
precision = symbol_info['precision']['amount']

amount_to_sell = exchange2.fetch_balance()["total"]["LTC"]
amount_to_buy = sub_account_money_balance / last_row["close"]
adjusted_amount_to_buy = truncate_to_three_decimals(amount_to_buy)

# buy_order = exchange1.create_order(symbol, 'market', 'buy', amount_to_buy, last_row["close"])
sell_order = exchange2.create_order(symbol, 'market', 'sell', amount_to_sell, last_row["close"])

# if symbol_info:
#     print(f"Minimálne množstvo: {symbol_info['limits']['amount']['min']}")
#     print(f"Počet desatinných miest: {symbol_info['precision']['amount']}")
#     print(f"Presnosť: {precision}")
#     print(f"Množstvo eur na účte: {sub_account_money_balance}")
#     print(f"Aktuálna cena: {last_row["close"]}")
#     print(f"Neupravený počet na kúpu: {amount_to_buy}")
#     print(f"Upravený počet na kúpu: {adjusted_amount_to_buy}")


