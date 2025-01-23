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

    timeframe = "1m"  # Časový rámec pre sviečky
    limit = 450  # Počet sviečok na získanie

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


ema_strategy_position = 1
bb_strategy_position = 0
scalping_strategy_position = 0


# def ma_strategy(df, crypto):
#     global position
#
#     # Výpočet kĺzavého priemeru
#     df["sma"] = df["close"].rolling(window=10).mean()
#
#     # Posledný riadok dát
#     last_row = df.iloc[-1]
#
#     # Stratégia
#     if last_row["close"] > last_row["sma"] and position == 0:
#         print("---BUY---")
#         print(f"({crypto}) BUY: {last_row['close']} - {last_row['timestamp']}")
#         print(f"Pretože cena {crypto} ({last_row["close"]}) pretla zdola nahor líniu sma ({last_row["sma"]})")
#         print("---")
#         position = 1
#     elif last_row["close"] < last_row["sma"] and position == 1:
#         print("---SELL---")
#         print(f"({crypto}) SELL: {last_row['close']} - {last_row['timestamp']}")
#         print(f"Pretože cena {crypto} ({last_row["close"]}) pretla zhora nadol líniu sma ({last_row["sma"]})")
#         print("---")
#         position = 0
#     else:
#         # Žiadna akcia, len čakáme
#         status = "Waiting to buy" if position == 0 else "Waiting to sell"
#         print(f"--{status}--")
#         print(f"({crypto}) {status} - {last_row['timestamp']}")
#         print(f"Pretože línia ceny ({last_row["close"]}) s líniou sma ({last_row["sma"]}) sa nepretli")
#         print("--")


# def bb_strategy(df, crypto, account_name):
#     global bb_strategy_position
#
#     # Nastavenie parametrov Bollinger Bands
#     window = 20
#     num_st_dev = 2
#
#     # Výpočet Bollinger Bands
#     df["sma"] = df["close"].rolling(window=window).mean()
#     df["st_dev"] = df["close"].rolling(window=window).std()  # Výpočet štandardnej odchýlky
#     df["upper_band"] = df["sma"] + (num_st_dev * df["st_dev"])
#     df["lower_band"] = df["sma"] - (num_st_dev * df["st_dev"])
#
#     # Posledný riadok dát
#     last_row = df.iloc[-1]
#
#     # Výpočet počtu kryptomeny na nákup
#     sub_account_balance = exchange2.fetch_balance()['total']['EUR']
#     amount_to_buy = sub_account_balance / last_row["close"]
#     adjusted_amount_to_buy = truncate_to_three_decimals(amount_to_buy)
#     # Výpočet počtu kryptomien na predaj
#     amount_to_sell = exchange2.fetch_balance()["total"]["LTC"]
#
#     # Stratégia
#     if last_row["close"] > last_row["upper_band"] and bb_strategy_position == 0:
#         print(f"{account_name}---BUY---")
#         print(f"{account_name} ({crypto}) BUY: {last_row['close']} - {last_row['timestamp']}")
#         print(f"{account_name} Pretože cena {crypto} ({last_row["close"]}) pretla zdola nahor hornú bollingerovú líniu "
#               f"{account_name} ({last_row["upper_band"]})")
#         print(f"{account_name} ---")
#         print()
#         buy_order = exchange2.create_order(symbol, 'market', 'buy', adjusted_amount_to_buy, last_row["close"])
#         bb_strategy_position = 1
#     elif last_row["close"] < last_row["lower_band"] and bb_strategy_position == 1:
#         print(f"{account_name} ---SELL---")
#         print(f"{account_name} ({crypto}) SELL: {last_row['close']} - {last_row['timestamp']}")
#         print(f"{account_name} Pretože cena {crypto} ({last_row["close"]}) pretla zhora nadol dolnú bollingerovú líniu "
#               f"{account_name} ({last_row["upper_band"]})")
#         print(f"{account_name} ---")
#         print()
#         sell_order = exchange2.create_order(symbol, 'market', 'sell', amount_to_sell, last_row["close"])
#         bb_strategy_position = 0
#     else:
#         # Žiadna akcia, len čakáme
#         status = "Waiting to buy" if bb_strategy_position == 0 else "Waiting to sell"
#         print(f"{account_name} --{status}--")
#         print(f"{account_name} ({crypto}) {status} - {last_row['timestamp']}")
#         print(f"{account_name} Pretože línia ceny ({last_row["close"]}) sa nepretla s dolnou bb líniou ({last_row["lower_band"]})"
#               f" ani s hornou bb líniou ({last_row["upper_band"]})")
#         print(f"{account_name} --")
#         print()


# def ema_strategy(df, crypto, account_name):
#     global ema_strategy_position
#
#     short = 7
#     long = 14
#
#     # Výpočet EMA línií
#     df["short_ema"] = df["close"].ewm(span=short, adjust=False).mean().round(2)
#     df["long_ema"] = df["close"].ewm(span=long, adjust=False).mean().round(2)
#
#     # Posledný riadok dát
#     last_row = df.iloc[-1]
#     prev_row = df.iloc[-2]
#
#     # Výpočet počtu kryptomien na nákup
#     sub_account_money_balance = exchange1.fetch_balance()['total']['EUR']
#     amount_to_buy = sub_account_money_balance / last_row["close"]
#     adjusted_amount_to_buy = truncate_to_three_decimals(amount_to_buy)
#     # Výpočet počtu kryptomien na predaj
#     amount_to_sell = exchange1.fetch_balance()["total"]["LTC"]
#     adjusted_amount_to_sell = truncate_to_three_decimals(amount_to_sell)
#
#     # Uprava línií pre zníženie počtu falošných signálov
#     # tolerance = 0
#     # last_lower_short_ema = last_row["short_ema"] * (1 - tolerance)
#     # last_higher_short_ema = last_row["short_ema"] * (1 + tolerance)
#     # last_lower_long_ema = last_row["long_ema"] * (1 - tolerance)
#     # last_higher_long_ema = last_row["long_ema"] * (1 + tolerance)
#     #
#     # prev_lower_short_ema = prev_row["short_ema"] * (1 - tolerance)
#     # prev_higher_short_ema = prev_row["short_ema"] * (1 + tolerance)
#     # prev_lower_long_ema = prev_row["long_ema"] * (1 - tolerance)
#     # prev_higher_long_ema = prev_row["long_ema"] * (1 + tolerance)
#
#     # can_buy = False
#     # can_sell = False
#     #
#     # # Stratégia
#     # if prev_row["short_ema"] < prev_row["long_ema"]:
#     #     can_buy = True
#     #     can_sell = False
#     #     print(f"can_buy = True")
#     # elif prev_row["short_ema"] > prev_row["long_ema"]:
#     #     can_buy = False
#     #     can_sell = True
#     #     print(f"can_sell = True")
#     # else:
#     #     # Nič nerobíme pretože EMA línie sú si rovné
#     #     pass
#
#     # Získanie posledného príkazu
#     order_history = exchange1.fetch_orders(symbol=symbol)
#
#     last_order_side = None
#     if order_history:  # Kontrola, či sú nejaké príkazy
#         last_order = order_history[-1]
#
#         timestamp = exchange1.iso8601(last_order['timestamp'])
#         utc_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
#
#         # Konverzia na miestny čas (napr. Europe/Bratislava)
#         local_timezone = pytz.timezone("Europe/Bratislava")
#         local_time = utc_time.astimezone(local_timezone)
#
#         last_order_side = last_order["side"]
#
#         # Zobrazenie poslednej objednávky
#         print(f"Order ID: {last_order['id']}")
#         print(f"Status: {last_order['status']}")
#         print(f"Side: {last_order['side']}")  # buy alebo sell
#         print(f"Price: {last_order['price']}")
#         print(f"Executed Qty: {last_order['filled']}")
#         print(f"Timestamp: {local_time}")
#         print()
#     else:
#         print("Neboli nájdené žiadne objednávky pre tento symbol.")
#         print()
#
#     # Stratégia
#     if last_row["short_ema"] > last_row["long_ema"] and ema_strategy_position == 0:
#         print(f"{account_name} ---BUY---")
#         print(f"{account_name} ({crypto}) BUY: {last_row['close']} - {last_row['timestamp']}")
#         print(f"{account_name} Pretože línia EMA{short} ({last_row["short_ema"]}) pretla zdola nahor líniu EMA{long} ({last_row["long_ema"]})")
#         print(f"{account_name} Pôvodná cena na nákup: {amount_to_buy}")
#         print(f"{account_name} Upravená cena na nákup (za ktorú sme naozaj kúpili): {adjusted_amount_to_buy}")
#         print(f"{account_name} ---")
#         print()
#         buy_order = exchange1.create_order(symbol, 'market', 'buy', adjusted_amount_to_buy, last_row["close"])
#         ema_strategy_position = 1
#     elif (last_row["short_ema"] < last_row["long_ema"] and
#             last_order_side == "buy"):
#         print(f"{account_name} ---SELL---")
#         print(f"{account_name} ({crypto}) SELL: {last_row['close']} - {last_row['timestamp']}")
#         print(f"{account_name} Pretože línia EMA{short} ({last_row["short_ema"]}) pretla zhora nadol líniu EMA{long} ({last_row["long_ema"]})")
#         print(f"{account_name} ---")
#         print()
#         sell_order = exchange1.create_order(symbol, 'market', 'sell', adjusted_amount_to_sell, last_row["close"])
#         ema_strategy_position = 0
#     else:
#         # Žiadna akcia, len čakáme
#         status = "Waiting to buy" if last_order_side == "sell" else "Waiting to sell"
#         print(f"{account_name} --{status}--")
#         print(f"{account_name} ({crypto}) {status} - {last_row['timestamp']}")
#         print(f"{account_name} Pretože krátka EMA línia {last_row["short_ema"]} sa nepretla s dlhou EMA líniou {last_row["long_ema"]}")
#         print(f"{account_name} --")
#         print()


def ema_strategy(df, crypto, account_name):
    global ema_strategy_position

    short = 3
    long = 14

    # Výpočet EMA línií
    df["short_ema"] = df["close"].ewm(span=short, adjust=False).mean().round(2)
    df["long_ema"] = df["close"].ewm(span=long, adjust=False).mean().round(2)

    # Posledný riadok dát
    last_row = df.iloc[-1]

    # Výpočet počtu kryptomien na nákup
    sub_account_money_balance = exchange1.fetch_balance()['total']['EUR']
    amount_to_buy = sub_account_money_balance / last_row["close"]
    adjusted_amount_to_buy = truncate_to_three_decimals(amount_to_buy)
    # Výpočet počtu kryptomien na predaj
    amount_to_sell = exchange1.fetch_balance()["total"]["LTC"]
    adjusted_amount_to_sell = truncate_to_three_decimals(amount_to_sell)

    # Uprava línií pre zníženie počtu falošných signálov
    tolerance = 0.0006
    last_lower_short_ema = last_row["short_ema"] * (1 - tolerance)
    last_higher_short_ema = last_row["short_ema"] * (1 + tolerance)
    last_lower_long_ema = last_row["long_ema"] * (1 - tolerance)
    last_higher_long_ema = last_row["long_ema"] * (1 + tolerance)

    # prev_lower_short_ema = prev_row["short_ema"] * (1 - tolerance)
    # prev_higher_short_ema = prev_row["short_ema"] * (1 + tolerance)
    # prev_lower_long_ema = prev_row["long_ema"] * (1 - tolerance)
    # prev_higher_long_ema = prev_row["long_ema"] * (1 + tolerance)

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
    if (last_lower_short_ema > last_higher_long_ema and
            ema_strategy_position == 0):
        print(f"{account_name} ---BUY---")
        print(f"{account_name} ({crypto}) BUY: {last_row['close']} - {last_row['timestamp']}")
        print(f"{account_name} Pretože línia EMA{short} ({last_row["short_ema"]}) pretla zdola nahor líniu EMA{long} ({last_row["long_ema"]})")
        print(f"{account_name} Pôvodná cena na nákup: {amount_to_buy}")
        print(f"{account_name} Upravená cena na nákup (za ktorú sme naozaj kúpili): {adjusted_amount_to_buy}")
        print(f"{account_name} ---")
        print()
        buy_order = exchange1.create_order(symbol, 'market', 'buy', adjusted_amount_to_buy, last_row["close"])
        ema_strategy_position = 1
    elif (last_higher_short_ema < last_lower_long_ema and
            last_order_side == "buy"):
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


def calculate_rsi(data, period=14):
    """
    Funkcia na výpočet RSI (Relative Strength Index) s knižnicou Pandas.

    Args:
        data (pd.DataFrame): DataFrame s cenami, musí obsahovať stĺpec 'close'.
        period (int): Počet období pre výpočet RSI.

    Returns:
        pd.Series: RSI hodnoty.
    """
    # Výpočet rozdielov medzi po sebe nasledujúcimi sviečkami
    delta = data['close'].diff()

    # Zisk a strata oddelene
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # Priemerný zisk a priemerná strata pomocou EMA (exponenciálneho priemeru)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    # Výpočet RS (pomocou exponenciálneho priemeru)
    rs = avg_gain / avg_loss

    # Výpočet RSI
    rsi = 100 - (100 / (1 + rs))

    return rsi


def bullish_engulfing_candle(last_closed_candle, prev_closed_candle):
    is_bullish_engulfing = False

    if (prev_closed_candle["close"] < prev_closed_candle["open"] and      # Predchádzajúca sviečka je červená
            last_closed_candle["close"] > last_closed_candle["open"] and  # Posledná sviečka je zelená
            last_closed_candle["open"] < prev_closed_candle["close"] and  # Otvorenie pod zatvorením predchádzajúcej sviečky
            last_closed_candle["close"] > prev_closed_candle["open"]):    # Zatvorenie nad otvorením predchádzajúcej sviečky
        is_bullish_engulfing = True

    return is_bullish_engulfing


def scalping_strategy(df, crypto, account_name):
    global scalping_strategy_position

    # Výpočet kĺzavého priemeru
    df["sma"] = df["close"].rolling(window=200).mean().round(2)

    # Získanie poslednej uzatvorenej sviečky (posledná sviečka je stále otvorená)
    last_closed_candle = df.iloc[-2]
    # Získanie sviečky pred ňou na zistenie Bullish Engulfing sviece
    prev_closed_candle = df.iloc[-3]

    # Posledný riadok dát
    last_row = df.iloc[-1]

    print(df.tail(200))

    # Výpočet RSI
    df["rsi"] = calculate_rsi(df)
    last_closed_rsi = df["rsi"].iloc[-2]  # RSI poslednej uzatvorenej sviečky

    # Výpočet počtu kryptomien na nákup
    sub_account_money_balance = exchange1.fetch_balance()['total']['EUR']
    amount_to_buy = sub_account_money_balance / last_row["close"]
    adjusted_amount_to_buy = truncate_to_three_decimals(amount_to_buy)
    # Výpočet počtu kryptomien na predaj
    amount_to_sell = exchange1.fetch_balance()["total"]["LTC"]
    adjusted_amount_to_sell = truncate_to_three_decimals(amount_to_sell)

    # Stratégia
    if (last_closed_candle["close"] > last_closed_candle["sma"] and
            last_closed_rsi > 50 and
            bullish_engulfing_candle(last_closed_candle, prev_closed_candle)):
        print(f"{account_name} ---BUY---")
        print(f"{account_name} ({symbol}) BUY: {last_row['close']} - {last_row['timestamp']}")
        print(
            f"{account_name} Pretože cena poslednej uzavretej sviece ({last_closed_candle["close"]}) > SMA200 ({last_closed_candle["sma"]})")
        print(f"{account_name} Pretože hodnota RSI ({last_closed_rsi}) > 50")
        print(f"{account_name} Pretože posledná uzatvorená svieca je Bullish Engulfing")
        print(f"{account_name} Upravená cena na nákup (za ktorú sme naozaj kúpili): {adjusted_amount_to_buy}")
        print(f"{account_name} ---")
        print()

        buy_order = exchange1.create_order(symbol, 'market', 'buy', adjusted_amount_to_buy, last_row["close"])

        scalping_strategy_position = 1

        buy_price = last_row["close"]

        # Vypočítať veľkosť tela Bullish Engulfing sviece
        body_size = abs(last_closed_candle["close"] - last_closed_candle["open"])

        # Stop Loss bude dvojnásobok veľkosti tela
        stop_loss_size = body_size * 2
        stop_loss_price = buy_price - stop_loss_size  # Stop loss nastavený pod aktuálnu cenu

        # Nastavenie príkazu na Stop Loss
        print(f"{account_name} Stop Loss nastavujeme na: {stop_loss_price}")
        exchange1.create_order(symbol, 'stop_loss_limit', 'sell', adjusted_amount_to_sell, stop_loss_price)

        # Nastavenie take profit
        take_profit_size = stop_loss_size * 2
        take_profit_price = buy_price + take_profit_size

        print(f"{account_name} Take Profit nastavujeme na: {take_profit_price}")
        exchange1.create_order(symbol, 'limit', 'sell', adjusted_amount_to_sell, take_profit_price)

        scalping_strategy_position = 1

    else:
        if scalping_strategy_position == 0:
            print()
            print(f"{account_name} Waiting to buy")  # Túto časť ešte treba poriešiť
            print()
        else:
            print()
            print(f"{account_name} Waiting to sell")


def run_strategy_for_account(exchange, strategy, symbol):
    while True:
        try:
            data = get_data(symbol)
            # Pridanie RSI do DataFrame
            data['RSI'] = calculate_rsi(data)
            strategy(data, symbol)
        except Exception as e:
            print(f"Error in strategy execution: {e}")
            print()
        time.sleep(20)  # Spustenie každú minútu


# run_strategy_for_account(exchange1, lambda df, symbol: ema_strategy(df, symbol, "EMA Strategy Account"), symbol)

# Vlákna pre každú stratégiu
# thread1 = threading.Thread(target=run_strategy_for_account, args=(exchange1, lambda df, symbol: ema_strategy(df, symbol, "EMA Strategy Account"), symbol))
thread1 = threading.Thread(target=run_strategy_for_account, args=(exchange1, lambda df, symbol: scalping_strategy(df, symbol, "Scalping Strategy Account"), symbol))
# thread2 = threading.Thread(target=run_strategy_for_account, args=(exchange2, lambda df, symbol: bb_strategy(df, symbol, "BB Strategy Account"), symbol))


# Spustenie vlákien
thread1.start()
# thread2.start()

# Voliteľne čakač na ich dokončenie
thread1.join()
# thread2.join()


