import ccxt
import config

binance = ccxt.binance({
    "enableRateLimit": True,
    "apiKey": config.API_KEY,
    "secret": config.API_SECRET
})

symbol = "XRP/EUR"
size = 4

balance = binance.fetch_balance()
# xrp_balance = balance["free"]["XRP"]
# print(f"Dostupný zostatok XRP: {xrp_balance}")

order = binance.create_market_buy_order(symbol, size)
print(order)

