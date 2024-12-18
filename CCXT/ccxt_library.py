import ccxt
import config

exchange = ccxt.binance({
    "apiKey": config.API_KEY,
    "secret": config.API_SECRET,
})


def get_bid_ask():
    eth_bin_book = exchange.fetch_order_book("ETH/EUR")
    eth_bid = eth_bin_book["bids"][0][0]
    eth_ask = eth_bin_book["asks"][0][0]
    print(f"The best bid: {eth_bid} the best ask {eth_ask}")
    return eth_bid, eth_ask


symbol = "ETH/EUR"
markets = exchange.load_markets()
symbol_info = markets[symbol]
min_notional = symbol_info['limits']['cost']['min']

mybid = get_bid_ask()[0] * 0.99  # Nastaví bid blízko aktuálnej ceny
pos_size = 0.004
order_value = mybid * pos_size

if order_value < min_notional:
    print(f"Objednávka má hodnotu {order_value}, čo je menej ako minimálna požiadavka {min_notional}. Zvýšte množstvo.")
    pos_size = min_notional / mybid

ticker = exchange.fetch_ticker(symbol)
current_price = ticker['last']
price_limit_low = current_price * 0.9
price_limit_high = current_price * 1.1

if not (price_limit_low <= mybid <= price_limit_high):
    print(f"Cena {mybid} je mimo povoleného rozsahu ({price_limit_low}, {price_limit_high}). Upravená na aktuálnu cenu.")
    mybid = current_price

params = {}
exchange.create_limit_buy_order(symbol, pos_size, mybid, params)
print("We just made an order.")

