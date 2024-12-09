import backtrader as bt
from backtrader.indicators import BollingerBands
import math


class BBandMacdStrategy(bt.Strategy):
    params = (
        ("period", 20),
        ("devfactor", 2),
        ("fast", 12),
        ("slow", 26),
        ("signal", 9),
        ("order_percentage", 1),
        ("ticker", "ORCL"),
        ("stop_loss", 0.95),
        ("take_profit", 1.10),
    )

    def __init__(self):
        self.bb = BollingerBands(period=self.params.period, devfactor=self.params.devfactor)

        self.fast_ema = bt.indicators.EMA(
            self.data.close, period=self.params.fast, plotname="12 day ema"
        )
        self.slow_ema = bt.indicators.EMA(
            self.data.close, period=self.params.slow, plotname="26 day ema"
        )
        self.signal_ema = bt.indicators.EMA(
            self.data.close, period=self.params.signal, plotname="9 day ema"
        )

        self.crossover = bt.indicators.CrossOver(self.fast_ema, self.slow_ema)

    def next(self):
        if self.position.size == 0:
            if self.data.close[0] > self.bb.lines.top[0]:
                if self.fast_ema < self.signal_ema and self.slow_ema < self.signal_ema:
                    if self.fast_ema[0] > self.fast_ema[-1] > self.fast_ema[-2]:
                        amount_to_invest = self.params.order_percentage * self.broker.cash
                        self.size = math.floor(amount_to_invest / self.data.close[0])
                        self.buy(size=self.size)
        else:
            if self.data.close[0] < self.bb.lines.bot[0]:
                if self.fast_ema > self.signal_ema and self.slow_ema > self.signal_ema:
                    if self.fast_ema[0] < self.fast_ema[-1] < self.fast_ema[-2]:
                        self.close()
