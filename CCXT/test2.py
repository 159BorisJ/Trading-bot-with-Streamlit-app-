import ccxt
import pandas as pd
import config
import time
import pytz
import threading
from datetime import datetime

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

    timeframe = "15m"  # Časový rámec pre sviečky
    limit = 50  # Počet sviečok na získanie

    for attempt in range(retries):
        try:
            # Pokus o získanie dát z Binance
            ohlcv = exchange1.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)  # Môžme použiť exchange1 pretože...
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


ema_strategy_position = 0


def ema_strategy(df, crypto, account_name):
    global ema_strategy_position

    short = 7
    long = 14

    # Výpočet EMA línií
    df["short_ema"] = df["close"].ewm(span=short, adjust=False).mean().round(2)
    df["long_ema"] = df["close"].ewm(span=long, adjust=False).mean().round(2)

    # Posledný riadok dát
    last_row = df.iloc[-1]
    prev_row = df.iloc[-2]

    # Výpočet počtu kryptomien na nákup
    sub_account_money_balance = exchange1.fetch_balance()['total']['EUR']
    amount_to_buy = sub_account_money_balance / last_row["close"]
    adjusted_amount_to_buy = truncate_to_three_decimals(amount_to_buy)
    # Výpočet počtu kryptomien na predaj
    amount_to_sell = exchange1.fetch_balance()["total"]["LTC"]
    adjusted_amount_to_sell = truncate_to_three_decimals(amount_to_sell)

    # Získanie posledného príkazu
    order_history = exchange1.fetch_orders(symbol=symbol)

    last_order_side = None
    if order_history:  # Kontrola, či sú nejaké príkazy
        last_order = order_history[-1]

        timestamp = exchange1.iso8601(last_order['timestamp'])
        utc_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

        # Konverzia na miestny čas (napr. Europe/Bratislava)
        local_timezone = pytz.timezone("Europe/Bratislava")
        local_time = utc_time.astimezone(local_timezone)

        last_order_side = last_order["side"]

        # Zobrazenie poslednej objednávky
        print(f"Order ID: {last_order['id']}")
        print(f"Status: {last_order['status']}")
        print(f"Side: {last_order['side']}")  # buy alebo sell
        print(f"Price: {last_order['price']}")
        print(f"Executed Qty: {last_order['filled']}")
        print(f"Timestamp: {local_time}")
        print()
    else:
        print("Neboli nájdené žiadne objednávky pre tento symbol.")
        print()

    # Stratégia
    if last_row["short_ema"] > last_row["long_ema"] and ema_strategy_position == 0:
        print(f"{account_name} ---BUY---")
        print(f"{account_name} ({crypto}) BUY: {last_row['close']} - {last_row['timestamp']}")
        print(f"{account_name} Pretože línia EMA{short} ({last_row["short_ema"]}) pretla zdola nahor líniu EMA{long} ({last_row["long_ema"]})")
        print(f"{account_name} Pôvodná cena na nákup: {amount_to_buy}")
        print(f"{account_name} Upravená cena na nákup (za ktorú sme naozaj kúpili): {adjusted_amount_to_buy}")
        print(f"{account_name} ---")
        print()
        buy_order = exchange1.create_order(symbol, 'market', 'buy', adjusted_amount_to_buy, last_row["close"])
        ema_strategy_position = 1
    elif last_row["short_ema"] < last_row["long_ema"] and ema_strategy_position == 1:
        print(f"{account_name} ---SELL---")
        print(f"{account_name} ({crypto}) SELL: {last_row['close']} - {last_row['timestamp']}")
        print(f"{account_name} Pretože línia EMA{short} ({last_row["short_ema"]}) pretla zhora nadol líniu EMA{long} ({last_row["long_ema"]})")
        print(f"{account_name} ---")
        print()
        sell_order = exchange1.create_order(symbol, 'market', 'sell', adjusted_amount_to_sell, last_row["close"])
        ema_strategy_position = 0
    else:
        # Žiadna akcia, len čakáme
        status = "Waiting to buy" if last_order_side == "sell" else "Waiting to sell"
        print(f"{account_name} --{status}--")
        print(f"{account_name} ({crypto}) {status} - {last_row['timestamp']}")
        print(f"{account_name} Pretože krátka EMA línia {last_row["short_ema"]} sa nepretla s dlhou EMA líniou {last_row["long_ema"]}")
        print(f"{account_name} --")
        print()


def run_strategy_for_account(exchange, strategy, symbol):
    while True:
        try:
            data = get_data(symbol)
            strategy(data, symbol)
        except Exception as e:
            print(f"Error in strategy execution: {e}")
            print()
        time.sleep(900)


# run_strategy_for_account(exchange1, lambda df, symbol: ema_strategy(df, symbol, "EMA Strategy Account"), symbol)

# Vlákna pre každú stratégiu
thread1 = threading.Thread(target=run_strategy_for_account, args=(exchange1, lambda df, symbol: ema_strategy(df, symbol, "EMA Strategy Account"), symbol))
# thread2 = threading.Thread(target=run_strategy_for_account, args=(exchange2, lambda df, symbol: bb_strategy(df, symbol, "BB Strategy Account"), symbol))


# Spustenie vlákien
thread1.start()
# thread2.start()

# Voliteľne čakač na ich dokončenie
thread1.join()
# thread2.join()


