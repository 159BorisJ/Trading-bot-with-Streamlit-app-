import ccxt
import pandas as pd
import time
import pytz
import config

exchange = ccxt.binance({
    "apiKey": config.MAIN_API_KEY,
    "secret": config.MAIN_API_SECRET,
    'enableRateLimit': True,
    "timeout": 30000,
})

symbol1 = "BTC/EUR"
symbol2 = "ETH/EUR"


def get_data(exchange, symbol, retries=5, delay=2):

    timeframe = "5m"  # Časový rámec pre sviečky
    limit = 50  # Počet sviečok na získanie

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


data = get_data(exchange, symbol1)
filtered_data = data[["timestamp", "close"]]

print(filtered_data)

