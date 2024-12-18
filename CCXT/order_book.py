import ccxt
import config

symbol = "BTC/EUR"

binance = ccxt.binance({
    "enableRateLimit": True,
    "apiKey": config.API_KEY,
    "secret": config.API_SECRET
})


def order_book():
    ob = binance.fetch_order_book(symbol)

    return ob


ob = order_book()
print(ob)


