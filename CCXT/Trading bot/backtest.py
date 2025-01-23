import backtrader as bt
import pandas as pd
import pytz
import time
import ccxt
import config2

exchange1 = ccxt.binance({
    "apiKey": config2.SUB_BB_API_KEY,
    "secret": config2.SUB_BB_API_SECRET,
    'enableRateLimit': True,
    "timeout": 30000,
})

symbol = "BTC/EUR"


def get_data(exchange, symbol, retries=5, delay=2):
    timeframe = "15m"
    limit = 6080  # 30 dní + 200 sviec

    for attempt in range(retries):
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            local_timezone = pytz.timezone("Europe/Bratislava")
            df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert(local_timezone)
            return df
        except Exception as e:
            print(f"Error: {e}. Retrying in {delay} seconds... (attempt {attempt + 1}/{retries})")
            time.sleep(delay)
    raise Exception(f"Failed to fetch data after {retries} retries.")


def convert_to_backtrader_format(df):
    df = df.rename(columns={'timestamp': 'datetime'})
    df.set_index('datetime', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']]
    df.index = pd.to_datetime(df.index)
    df.index = df.index.tz_localize(None)
    return df


class MACDStrategySLTP(bt.Strategy):
    params = (
        ('stop_loss_percent', 1.4),
        ('take_profit_percent', 2.3),
        ('macd_me1', 12),
        ('macd_me2', 26),
        ('macd_signal', 9),
        ('ema_period', 200)
    )

    def __init__(self):
        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.params.macd_me1,
            period_me2=self.params.macd_me2,
            period_signal=self.params.macd_signal
        )
        self.long_ema = bt.indicators.EMA(self.data.close, period=self.params.ema_period)
        self.stop_loss_price = None
        self.take_profit_price = None

    def next(self):
        current_price = self.data.close[0]
        cash = self.broker.get_cash()

        if not self.position:
            if (self.macd.macd[0] > self.macd.signal[0] and
                    self.macd.macd[-1] < self.macd.signal[-1] and
                    self.macd.macd[0] < 0 and self.macd.signal[0] < 0 and
                    self.data.close[0] > self.long_ema[0]):

                # Výpočet zlomkového množstva
                size = cash / current_price
                self.buy(size=size)
                self.stop_loss_price = current_price * (1 - self.params.stop_loss_percent / 100)
                self.take_profit_price = current_price * (1 + self.params.take_profit_percent / 100)
                print(f"Buying {size:.6f} units at {current_price}")

        elif self.position:
            # Kontrola stop loss a take profit
            if current_price <= self.stop_loss_price or current_price >= self.take_profit_price:
                self.close()
                print(f"Selling at {current_price}")


class SMACrossover(bt.Strategy):
    params = (
        ('sma_short_period', 10),
        ('sma_long_period', 30),
    )

    def __init__(self):
        self.sma_short = bt.indicators.SMA(self.data.close, period=self.params.sma_short_period)
        self.sma_long = bt.indicators.SMA(self.data.close, period=self.params.sma_long_period)

    def next(self):
        current_price = self.data.close[0]
        cash = self.broker.get_cash()

        if not self.position:  # No open position
            if self.sma_short[0] > self.sma_long[0]:
                # Výpočet zlomkového množstva
                size = cash / current_price
                self.buy(size=size)
        else:  # Position is open
            if self.sma_short[0] < self.sma_long[0]:
                self.close()


# Backtesting setup
cerebro = bt.Cerebro()
market_data = get_data(exchange1, symbol)
backtest_data = convert_to_backtrader_format(market_data)
data_feed = bt.feeds.PandasData(dataname=backtest_data)

cerebro.adddata(data_feed)
cerebro.addstrategy(MACDStrategySLTP)
cerebro.broker.set_cash(10000)
cerebro.run()
cerebro.plot()
