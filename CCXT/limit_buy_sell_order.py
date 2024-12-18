import ccxt
import config

binance = ccxt.binance({
    "enableRateLimit": True,
    "apiKey": config.API_KEY,
    "secret": config.API_SECRET
})

symbol = "XRP/EUR"
size = 4
bid = 2.4
ask = 2.445

# create limit BUY order
# order = binance.create_limit_buy_order(symbol, size, bid)
# print(order)

# create limit SELL order
order = binance.create_limit_sell_order(symbol, size, ask)
print(order)

