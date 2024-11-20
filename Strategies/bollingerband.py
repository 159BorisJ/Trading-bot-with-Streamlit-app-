import backtrader as bt
from backtrader.indicators import BollingerBands
import math


class BolingerBandStrategy(bt.Strategy):
    params = (("period", 20), ("devfactor", 2), ("order_percentage", 0.95))

    def __init__(self):
        self.bb = BollingerBands(period=self.params.period, devfactor=self.params.devfactor)

    def next(self):
        if self.position.size == 0:
            if self.data.close[0] > self.bb.lines.top[0]:
                amount_to_invest = self.params.order_percentage * self.broker.cash
                self.size = math.floor(amount_to_invest / self.data.close[0])
                self.buy(size=self.size)
        else:
            if self.data.close[0] < self.bb.lines.bot[0]:
                self.close()

