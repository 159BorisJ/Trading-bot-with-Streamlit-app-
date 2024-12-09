import sys
import time
import json

# Cesta k virtuálnemu prostrediu
venv_path = r"C:\Users\admin\Desktop\Trading app\venv\Lib\site-packages"
sys.path.append(venv_path)

from binance.client import Client
from binance.enums import *

# Tvoje API kľúče z testnetu
api_key = "H1wkVXKJIWO4erTBniTMolvKOLrLLbh6mu2zPQrDZ9pCYTexKB75dqJDvdhhe3k3"
api_secret = "ftdJF2501Pp2jAdAIxONNM5fAmBltZESRSkLu3lFdo9E2qg1PS9XpZOtWFAQnLYK"

# Inicializuj klienta
client = Client(api_key, api_secret)

# Vyber symbol (napr. 'BTCUSDT')
symbol = 'BTCUSDT'

# Urči časový interval a počet sviečok (napr. 1 hodina, posledných 100 sviečok)
interval = Client.KLINE_INTERVAL_1DAY
limit = 1

# Získaj historické sviečky
klines = client.get_historical_klines(symbol, interval, limit=limit)

# Zobraz výsledky
for kline in klines:
    print(f"Otvorenie: {kline[1]}, Najvyššia: {kline[2]}, Najnižšia: {kline[3]}, Zatvorenie: {kline[4]}")

