import os, sys, argparse
from tabulate import tabulate
import pandas as pd
import backtrader as bt

from Strategies.BuyHold import BuyHold
from Strategies.golden_cross import GoldenCross
from Strategies.macd import MACD
from Strategies.bollingerband import BolingerBandStrategy
from Strategies.stochastic_oscillator import StochasticOscillatorStrategy
from Strategies.bb_and_stochastic_oscilator import BBAndStochOscStrategy
from Strategies.bb_and_macd import BBandMacdStrategy


# stock = "ETH-USD"
#
# cerebro = bt.Cerebro()
# cerebro.broker.setcash(10000)
#
# stock_prices = pd.read_csv(f"Data-cryptos/{stock}.csv", index_col="Date", parse_dates=True)
#
# feed = bt.feeds.PandasData(dataname=stock_prices)
# cerebro.adddata(feed)
#
# cerebro.addstrategy(BolingerBandStrategy)
#
# cerebro.run()
#
# cerebro.plot()

stocks = ["AAPL", "AMZN", "BA", "CVX", "GME", "INTC", "NVDA", "ORCL", "T", "TSLA", "XOM", "IBM", "GE", "KO", "MCD", "PG",
          "PEP", "JNJ", "WMT"]

cryptos = ["BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD", "SOL-USD", "DOGE-USD", "DOT-USD", "LTC-USD", "AVAX-USD",
           "MATIC-USD", "UNI-USD", "ATOM-USD", "FTM-USD"]

strategies = [BolingerBandStrategy, BBandMacdStrategy, GoldenCross, MACD]

comodities = cryptos

# Inicializácia dát pre tabuľku
data = []

# Naplnenie riadkov tabuľky
for c in comodities:
    row = {"comodities": c}  # Pridaj názov komodity do stĺpca "comodities"
    for s in strategies:
        row[s.__name__] = 0  # Inicializácia výsledkov pre každú stratégiu
    data.append(row)


def format_number(value):
    return f"{value:,.2f}".replace(',', ' ').replace('.', ',')


directory_name = 0
if comodities == stocks:
    directory_name = "stocks"
elif comodities == cryptos:
    directory_name = "cryptos"

start_date = 0
end_date = 0
if comodities == stocks:
    start_date = "1995-01-01"
    end_date = "2014-12-31"
elif comodities == cryptos:
    start_date = "2013-01-01"
    end_date = "2023-12-31"

# Zoznam na uchovávanie výsledkov pre každú stratégiu
strategy_results = {strategy.__name__: [] for strategy in strategies}

buy_hold_portfolio_values = []
for c in comodities:
    # Inicializácia pre BuyHold
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(10000)

    comodity_prices = pd.read_csv(f"Data-{directory_name}/{c}.csv", index_col="Date", parse_dates=True)
    feed = bt.feeds.PandasData(dataname=comodity_prices)
    cerebro.adddata(feed)

    df = pd.read_csv(f"Data-{directory_name}/{c}.csv", parse_dates=True)
    first_date = df.iloc[0]["Date"]
    last_date = df.iloc[-1]["Date"]
    period = f"{first_date}_{last_date}"

    cerebro.addstrategy(BuyHold)
    cerebro.run()
    final_portfolio_value = cerebro.broker.get_value()
    buy_hold_portfolio_values.append(final_portfolio_value)

    # Formátovanie výsledku pred pridaním do tabuľky
    formatted_value = format_number(final_portfolio_value)

    # Pridanie výsledku do tabuľky
    for row in data:
        if row["comodities"] == c:
            row["BuyHold"] = formatted_value
            row["Period"] = period

# Iterovanie cez stratégie a akcie
for i, c in enumerate(comodities):
    for strategy in strategies:
        # Inicializácia pre inú stratégiu (nie BuyHold)
        cerebro = bt.Cerebro()
        cerebro.broker.setcash(10000)

        comodity_prices = pd.read_csv(f"Data-{directory_name}/{c}.csv", index_col="Date", parse_dates=True)
        feed = bt.feeds.PandasData(dataname=comodity_prices)
        cerebro.adddata(feed)

        cerebro.addstrategy(strategy)
        cerebro.run()
        final_portfolio_value = cerebro.broker.get_value()

        # Formátovanie výsledku pred pridaním do tabuľky
        formatted_value = format_number(final_portfolio_value)

        # Pridanie výsledku do tabuľky
        for row in data:
            if row["comodities"] == c:
                row[strategy.__name__] = formatted_value

        # Uloženie výsledku do príslušného zoznamu pre danú stratégiu
        strategy_results[strategy.__name__].append(final_portfolio_value)

        print(f"For {c} in strategy {strategy.__name__} is final portfolio value: {final_portfolio_value:,.2f}".replace(',', ' ').replace('.', ','))
        print(f"Buy and Hold strategy final value is: {buy_hold_portfolio_values[i]:,.2f}".replace(',', ' ').replace('.',','))

# Vypísanie celkového súčtu výsledkov pre každú stratégiu
for strategy, results in strategy_results.items():
    total_value = sum(results)
    print(f"\nTotal portfolio value for strategy {strategy}: {total_value:,.2f}".replace(',', ' ').replace('.', ','))

# Výpočet súčtov pre každú stratégiu
totals = {"comodities": "Total"}  # Stĺpec "comodities" bude obsahovať text "Total"
for strategy in strategies + [BuyHold]:
    strategy_name = strategy.__name__ if strategy != BuyHold else "BuyHold"
    # Súčet hodnôt v stĺpci stratégie
    total = sum(float(row[strategy_name].replace(' ', '').replace(',', '.')) for row in data)
    # Formátovanie súčtu
    totals[strategy_name] = format_number(total)

# Pridanie súčtov ako posledného riadku tabuľky
data.append(totals)

# Vypísanie tabuľky
print("\nFinal Results Table:")
print(tabulate(data, headers="keys", tablefmt="fancy_grid"))


