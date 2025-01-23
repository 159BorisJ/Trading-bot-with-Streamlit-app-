import os, sys, argparse
from tabulate import tabulate
import pandas as pd
import backtrader as bt

from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font

from Strategies.BuyHold import BuyHold
from Strategies.golden_cross import GoldenCross
from Strategies.macd import MACD
from Strategies.bollingerband import BollingerBandStrategy
from Strategies.stochastic_oscillator import StochasticOscillatorStrategy
from Strategies.bb_and_stochastic_oscilator import BBAndStochOscStrategy
from Strategies.bb_and_macd import BBandMacdStrategy


# c = "BTC-USD"
#
# cerebro = bt.Cerebro()
# cerebro.broker.setcash(10000)
#
# stock_prices = pd.read_csv(
#     f"Data-cryptos/{c}.csv", index_col="Date", parse_dates=True)
#
# feed = bt.feeds.PandasData(dataname=stock_prices)
# cerebro.adddata(feed)
#
# cerebro.addstrategy(BolingerBandStrategy)
#
# cerebro.run()
#
# cerebro.plot()

stocks = [
    "AAPL", "AMZN", "BA", "CVX", "GME", "INTC", "NVDA", "ORCL", "T", "TSLA", "XOM",
    "IBM", "GE", "KO", "MCD", "PG", "PEP", "JNJ", "WMT", "MSFT", "GOOGL", "META",
    "NFLX", "ADBE", "CSCO", "AVGO", "AMD", "QCOM", "TXN", "SPY", "SAP", "V", "JPM",
    "MA", "ASML", "DIS", "NKE", "HD", "UNH", "PFE", "MRK", "ABBV", "CRM", "TMO", "VZ",
    "CMCSA", "BAC", "WFC", "C", "GS", "MS", "AMGN", "COST", "CVS", "DHR", "ABT", "LLY",
    "RTX", "HON", "LIN", "PM", "UNP", "NEE", "SBUX", "MDT", "NOW", "BLK", "ELV", "PLD",
    "INTU", "UPS", "AXP", "CAT", "MMM", "DUK", "BDX", "ZTS", "LOW", "AMT", "ADP", "ISRG",
    "CL", "TGT", "ECL", "ITW", "BK", "DE", "GILD", "CME", "NOC", "SO", "CI", "APD", "SPGI",
    "SYK", "USB", "HUM", "NSC", "TJX", "AON"
]

cryptos = [
    "BTC-USD", "ETH-USD", "BNB-USD", "ADA-USD", "XRP-USD", "SOL-USD", "DOGE-USD",
    "DOT-USD", "MATIC-USD", "LTC-USD", "TRX-USD", "AVAX-USD", "UNI-USD",
    "LINK-USD", "XLM-USD", "ATOM-USD", "ALGO-USD", "FIL-USD", "VET-USD", "ICP-USD",
    "APE-USD", "GRT-USD", "NEAR-USD", "FTM-USD", "SAND-USD", "AXS-USD", "THETA-USD",
    "EGLD-USD", "HBAR-USD", "MANA-USD", "LEO-USD", "QNT-USD", "CAKE-USD", "EOS-USD",
    "RUNE-USD", "KAVA-USD", "ENJ-USD", "ONE-USD", "CHZ-USD", "ZIL-USD", "BAT-USD",
    "KSM-USD", "CRO-USD", "WBTC-USD", "LRC-USD", "CELO-USD", "MKR-USD", "YFI-USD",
    "SNX-USD", "CRV-USD", "BAL-USD", "ZRX-USD", "REN-USD", "UMA-USD",
    "BAND-USD", "KNC-USD", "ANKR-USD", "OCEAN-USD", "AR-USD", "ICX-USD", "QTUM-USD",
    "WAVES-USD", "GALA-USD", "FTT-USD", "SUSHI-USD", "SRM-USD", "LUNA-USD", "XTZ-USD",
    "CEL-USD", "AAVE-USD", "HT-USD", "OKB-USD", "PERP-USD", "HNT-USD", "FTM-USD",
    "BTT-USD", "STX-USD", "COTI-USD", "NEO-USD", "RVN-USD", "ZEC-USD", "DASH-USD",
    "XMR-USD", "SC-USD", "XEM-USD", "ONT-USD", "IOST-USD", "GNO-USD", "BNT-USD",
    "CVC-USD", "SXP-USD", "NEXO-USD", "OGN-USD", "TWT-USD", "DYDX-USD", "CHSB-USD",
    "ALPHA-USD", "POLY-USD", "RNDR-USD", "MINA-USD"
]

strategies = [
    BollingerBandStrategy, BBandMacdStrategy,
    GoldenCross, MACD, StochasticOscillatorStrategy
]

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
start_date = 0
end_date = 0
excel_name = 0
if comodities == stocks:
    directory_name = "stocks"
    start_date = "1995-01-01"
    end_date = "2014-12-31"
elif comodities == cryptos:
    directory_name = "cryptos"
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

# Iterovanie cez stratégie a aktíva
for i, c in enumerate(comodities):
    for strategy in strategies:
        # Inicializácia pre stratégie na testovanie
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
# for strategy, results in strategy_results.items():
#     total_value = sum(results)
#     print(f"\nTotal portfolio value for strategy {strategy}: {total_value:,.2f}".replace(',', ' ').replace('.', ','))

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

# print("\nFinal Results Table:")
# print(tabulate(data, headers="keys", tablefmt="fancy_grid"))


# Porovnanie úspešnosti stratégií
strategy_success = {strategy.__name__: {"beat_buy_hold": 0, "mid": 0, "bellow_10000": 0} for strategy in strategies}

for i, c in enumerate(comodities):
    buy_hold_value = buy_hold_portfolio_values[i]  # Hodnota BuyHold pre danú komoditu
    for strategy in strategies:
        # Hodnota stratégie pre danú komoditu
        final_value = strategy_results[strategy.__name__][i]

        # 1. Prekonanie stratégie BuyHold
        if final_value > buy_hold_value:
            strategy_success[strategy.__name__]["beat_buy_hold"] += 1

        elif 10000 < final_value < buy_hold_value:
            strategy_success[strategy.__name__]["mid"] += 1

        # 2. Portfólio v mínuse (pod 10 000)
        elif final_value < 10000:
            strategy_success[strategy.__name__]["bellow_10000"] += 1

# Výpis úspešnosti stratégií
print("\nMiera úspešnosti stratégií:")
for strategy, success in strategy_success.items():
    print(f"{strategy}:")
    print(f"  - Portfóliá, ktoré prekonali BuyHold: {success["beat_buy_hold"]}")
    print(f"  - Portfóliá, ktoré neprekonali BuyHold ale neskončili pod 10 000: {success["mid"]}")
    print(f"  - Portfóliá, ktoré skončili pod 10 000: {success["bellow_10000"]}")


# Uloženie tabuľky do Excelu
df = pd.DataFrame(data)

excel_filename = f"final_results_{directory_name}.xlsx"
df.to_excel(excel_filename, index=False)

print()
print(f"Tabuľka bola uložená do súboru {excel_filename}")




