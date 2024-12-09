import math
import backtrader as bt


class GoldenCross(bt.Strategy):
    params = (
        ("fast", 50),
        ("slow", 200),
        ("order_percentage", 1),
    )

    def __init__(self):
        self.fast_moving_average = bt.indicators.SMA(
            self.data.close, period=self.params.fast, plotname="50 day moving average"
        )
        self.slow_moving_average = bt.indicators.SMA(
            self.data.close, period=self.params.slow, plotname="200 day moving average"
        )
        self.crossover = bt.indicators.CrossOver(self.fast_moving_average, self.slow_moving_average)

    def next(self):
        if self.position.size == 0:  # Ak nemám otvorenú pozíciu
            if self.crossover > 0:  # Signál na nákup
                amount_to_invest = self.params.order_percentage * self.broker.cash
                self.size = math.floor(amount_to_invest / self.data.close[0])

                # print(f"Buy {self.size} shares of {self.params.ticker} at {self.data.close[0]}")

                self.buy(size=self.size)

        elif self.position.size > 0:  # Ak už máme otvorenú pozíciu
            if self.crossover < 0:  # Signál na predaj
                # print(f"Sell {self.size} shares of {self.params.ticker} at {self.data.close[0]}")
                self.close()

