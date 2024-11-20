import pandas as pd
import backtrader as bt
import yfinance as yf
from datetime import datetime
from Strategies.bb_and_macd_multiple_stock import BBandMacdMultipleStockStrategy


cerebro = bt.Cerebro()

stocks = ["AAPL", "AMZN", "BA", "CVX", "GE"]
for stock in stocks:
    data = pd.read_csv(f"Data-stocks/{stock}_1995-01-01-2014-12-31.csv", index_col="Date", parse_dates=True)
    feed = bt.feeds.PandasData(dataname=data)
    cerebro.adddata(feed)

cerebro.broker.setcash(10000)

cerebro.addstrategy(BBandMacdMultipleStockStrategy)

cerebro.run()

final_value = cerebro.broker.get_value()
print(final_value)

