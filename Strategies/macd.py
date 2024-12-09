import backtrader as bt
import math


class MACD(bt.Strategy):
    params = (
        ("fast", 12),
        ("slow", 26),
        ("signal", 9),
        ("order_percentage", 1),
        ("ticker", "ORCL"),
        ("stop_loss", 0.95),
        ("take_profit", 1.10),
    )

    def __init__(self):
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

        self.entry_price = None

    def next(self):
        if self.position.size == 0:  # Ak nemám otvorenú pozíciu
            if self.crossover == 1:  # Ak rýchla EMA pretne pomalú EMA zdola
                if self.fast_ema < self.signal_ema and self.slow_ema < self.signal_ema:  # Ak sú obe línie EMA pod líniou signálnou líniou
                    if self.fast_ema > self.slow_ema * 1.002:
                        amount_to_invest = self.params.order_percentage * self.broker.cash
                        self.size = math.floor(amount_to_invest / self.data.close[0])

                        # print(f"Buy {self.size} shares of {self.params.ticker} at {self.data.close[0]}")

                        self.buy(size=self.size)
                        self.entry_price = self.data.close[0]

        elif self.position.size > 0:  # Ak už máme otvorenú pozíciu
            current_price = self.data.close[0]

            # # Kontrola stop loss
            # if current_price <= self.entry_price * self.params.stop_loss:
            #     print(f"Stop Loss Triggered: Sell {self.size} shares of {self.params.ticker} at {current_price}")
            #     self.close()
            #     self.entry_price = None  # Reset entry_price po zatvorení pozície

            # # Kontrola take profit
            # elif current_price >= self.entry_price * self.params.take_profit:
            #     print(f"Take Profit Triggered: Sell {self.size} shares of {self.params.ticker} at {current_price}")
            #     self.close()
            #     self.entry_price = None  # Reset entry_price po zatvorení pozície

            if self.crossover == -1:  # Ak rýchla EMA pretne pomalú EMA zhora
                if self.fast_ema > self.signal_ema and self.slow_ema > self.signal_ema:  # Ak sú obe EMA línie nad signálnou líniou
                    if self.fast_ema * 1.002 < self.slow_ema:
                        # print(f"Sell {self.size} shares of {self.params.ticker} at {self.data.close[0]}")
                        self.close()
                        self.entry_price = None  # Reset entry_price po zatvorení pozície


