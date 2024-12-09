import backtrader as bt
from backtrader.indicators import BollingerBands
import math


class BBAndStochOscStrategy(bt.Strategy):
    params = (
        ("period", 20),
        ("devfactor", 2),
        ("order_percentage", 1),
        ('k_period', 14),  # Perioda pre výpočet %K
        ('d_period', 3),  # Perioda pre výpočet %D (hladká čiara)
        ('upper_limit', 80),  # Hranica pre prekúpenosť
        ('lower_limit', 20),  # Hranica pre prepredanosť
    )

    def __init__(self):
        self.bb = BollingerBands(period=self.params.period, devfactor=self.params.devfactor)

        self.stochastic = bt.indicators.Stochastic(
            self.data,
            period=self.params.k_period,
            period_dfast=self.params.d_period,
            safediv=True  # Zabráni deleniu nulou
        )

    def next(self):
        if self.position.size == 0:
            if self.data.close[0] > self.bb.lines.top[0]:
                # Prepredanosť: %K < lower_limit a %D < lower_limit
                if self.stochastic.percK < self.params.lower_limit and self.stochastic.percD < self.params.lower_limit:
                    amount_to_invest = self.params.order_percentage * self.broker.cash
                    self.size = math.floor(amount_to_invest / self.data.close[0])
                    self.buy(size=self.size)
        else:
            if self.data.close[0] < self.bb.lines.bot[0]:
                # Prekúpenosť: %K > upper_limit a %D > upper_limit
                if self.stochastic.percK > self.params.upper_limit and self.stochastic.percD > self.params.upper_limit:
                    self.sell(size=self.size)

