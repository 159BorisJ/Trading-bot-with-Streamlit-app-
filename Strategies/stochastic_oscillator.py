import backtrader as bt
import math


class StochasticOscillatorStrategy(bt.Strategy):
    params = (
        ('k_period', 14),  # Perioda pre výpočet %K
        ('d_period', 3),   # Perioda pre výpočet %D (hladká čiara)
        ('upper_limit', 80),  # Hranica pre prekúpenosť
        ('lower_limit', 20),  # Hranica pre prepredanosť
        ("order_percentage", 0.95),
    )

    def __init__(self):
        # Inicializácia Stochastic Oscillator indikátora
        self.stochastic = bt.indicators.Stochastic(
            self.data,
            period=self.params.k_period,
            period_dfast=self.params.d_period,
            safediv=True  # Zabráni deleniu nulou
        )

    def next(self):
        # Prepredanosť: %K < lower_limit a %D < lower_limit
        if self.stochastic.percK < self.params.lower_limit and self.stochastic.percD < self.params.lower_limit:
            if not self.position:  # Ak ešte nemáme otvorenú pozíciu
                amount_to_invest = self.params.order_percentage * self.broker.cash
                self.size = math.floor(amount_to_invest / self.data.close[0])
                self.buy(size=self.size)  # Otvorenie dlhej pozície (kúpa)

        # Prekúpenosť: %K > upper_limit a %D > upper_limit
        elif self.stochastic.percK > self.params.upper_limit and self.stochastic.percD > self.params.upper_limit:
            if self.position:  # Ak máme otvorenú pozíciu
                self.close()  # Uzavretie pozície (predaj)

