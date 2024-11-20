import backtrader as bt
from backtrader.indicators import BollingerBands
import math


class BBandMacdMultipleStockStrategy(bt.Strategy):
    params = (
        ("period", 20),
        ("devfactor", 2),
        ("order_percentage", 0.95),
        ("fast", 12),
        ("slow", 26),
        ("signal", 9),
        ("order_percentage", 0.95),
        ("ticker", "ORCL"),
        ("stop_loss", 0.95),
        ("take_profit", 1.10),
    )

    def __init__(self):
        # Ukladanie indikátorov pre každý dátový feed
        self.indicators = {}
        for d in self.datas:
            self.indicators[d] = {
                "bb": BollingerBands(d.close, period=self.params.period, devfactor=self.params.devfactor),
                "fast_ema": bt.indicators.EMA(d.close, period=self.params.fast),
                "slow_ema": bt.indicators.EMA(d.close, period=self.params.slow),
                "signal_ema": bt.indicators.EMA(d.close, period=self.params.signal),
                "crossover": bt.indicators.CrossOver(
                    bt.indicators.EMA(d.close, period=self.params.fast),
                    bt.indicators.EMA(d.close, period=self.params.slow),
                ),
            }

    def next(self):
        for d in self.datas:
            ind = self.indicators[d]  # Získaj indikátory pre konkrétny dátový feed

            # Ak nie je žiadna pozícia, hľadáme nákupný signál
            if not self.getposition(d).size:
                if d.close[0] > ind["bb"].lines.top[0]:  # Cena nad horným pásmom
                    if ind["fast_ema"][0] > ind["fast_ema"][-1] > ind["fast_ema"][-2]:  # EMA stúpa
                        amount_to_invest = self.params.order_percentage * self.broker.cash
                        size = math.floor(amount_to_invest / d.close[0])
                        self.buy(data=d, size=size)  # Kúp konkrétny dátový feed

            # Ak existuje pozícia, hľadáme predajný signál
            else:
                if d.close[0] < ind["bb"].lines.bot[0]:  # Cena pod spodným pásmom
                    if ind["fast_ema"][0] < ind["fast_ema"][-1] < ind["fast_ema"][-2]:  # EMA klesá
                        self.close(data=d)  # Zatvor pozíciu pre konkrétny dátový feed

