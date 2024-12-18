import ccxt
import config
import time

binance = ccxt.binance({
    "enableRateLimit": True,
    "apiKey": config.API_KEY,
    "secret": config.API_SECRET
})

symbol = "XRP/EUR"
size = 6
go = True
sleep = 20


def get_bid_ask():
    book = binance.fetch_order_book(symbol)
    bid = book["bids"][0][0]
    ask = book["asks"][0][0]

    print(f"best bid for {symbol} is {bid}")
    print(f"best ask for {symbol} is {ask}")

    return ask, bid


get_bid_ask()

while go:
    bid = get_bid_ask()[1]
    ask = get_bid_ask()[0]
    print(bid)

    lowbid = bid * 0.99

    # create order
    binance.create_limit_buy_order(symbol, size, lowbid)

    print(f"Just made an order, now sleeping for {sleep} seconds")
    time.sleep(sleep)
