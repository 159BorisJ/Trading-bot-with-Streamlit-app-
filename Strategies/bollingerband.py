import backtrader as bt
from backtrader.indicators import BollingerBands
import math


class BolingerBandStrategy(bt.Strategy):
    params = (("period", 20), ("devfactor", 2), ("order_percentage", 1))

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

    # def notify_order(self, order):
    #     if order.status in [order.Completed]:
    #         typ = "Nákup" if order.isbuy() else "Predaj"
    #         print(f"=== {typ} ===")
    #         print(f"Dátum: {self.data.datetime.date(0)}")
    #         print(f"Cena použitého obchodu: {order.executed.price:.2f}")
    #         print(f"Veľkosť (počet jednotiek): {order.executed.size}")
    #         print(f"Poplatky: {order.executed.comm:.2f}")
    #
    #         # Výpis detailov o hotovosti a hodnote portfólia
    #         print(f"Hotovosť pred {typ.lower()}: {self.broker.get_cash():.2f}")
    #         # print(f"Hodnota portfólia pred {typ.lower()}: {self.broker.get_value():.2f}")
    #         print(f"Skutočná hodnota transakcie: {order.executed.size * order.executed.price:.2f}")
    #
    #     elif order.status in [order.Submitted, order.Accepted]:
    #         # Objednávka bola prijatá alebo odoslaná na trh
    #         pass
    #     elif order.status in [order.Canceled, order.Margin, order.Rejected]:
    #         print(f"Objednávka zrušená/odmietnutá: {order.status}")
    #
    # def notify_trade(self, trade):
    #     if trade.isclosed:  # Trade closed
    #         # print(f"=== Obchod uzavretý ===")
    #         # print(f"Dátum uzavretia: {self.data.datetime.date(0)}")
    #         # print(f"Dátum otvorenia: {bt.num2date(trade.dtopen)}")
    #         # print(f"Koncová cena: {self.data.close[0]:.2f}")
    #         print(f"Zisk/Strata: {trade.pnl:.2f}")
    #         # print(f"Poplatky: {trade.commission:.2f}")
    #
    #         # Detailné informácie o portfóliu po uzavretí obchodu
    #         # print(f"Hotovosť po uzavretí obchodu: {self.broker.get_cash():.2f}")
    #         # print(f"Hodnota portfólia po uzavretí obchodu: {self.broker.get_value():.2f}")
    #     # elif trade.isopen:  # Trade opened
    #     #     print(f"=== Obchod otvorený ===")
    #     #     print(f"Dátum otvorenia: {self.data.datetime.date(0)}")
    #     #     print(f"Kúpna cena: {self.data.close[0]:.2f}")
    #     #
    #     #     # Výpis stavu portfólia pri otvorení obchodu
    #     #     print(f"Hotovosť po otvorení obchodu: {self.broker.get_cash():.2f}")
    #     #     print(f"Hodnota portfólia po otvorení obchodu: {self.broker.get_value():.2f}")



