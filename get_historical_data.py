import yfinance as yf
import pandas as pd
import os

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


# cryptos = ["BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD", "SOL-USD", "DOGE-USD", "DOT-USD", "LTC-USD", "AVAX-USD",
#            "MATIC-USD", "UNI-USD", "ATOM-USD", "FTM-USD"]

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

comodities = stocks

directory_name = 0
start_date = 0
end_date = 0
if comodities == stocks:
    directory_name = "stocks"
    start_date = "1995-01-01"
    end_date = "2014-12-31"
elif comodities == cryptos:
    directory_name = "cryptos"
    start_date = "2013-01-01"
    end_date = "2024-12-01"


for c in comodities:
    ticker_symbol = c

    # Načítavanie historických dát
    data = yf.download(ticker_symbol, start=start_date, end=end_date)

    # Resetovanie indexu, aby bol dátum ako stĺpec
    data.reset_index(inplace=True)
    data["Date"] = data["Date"].dt.strftime('%Y-%m-%d')

    # # Uprava názvou stĺpcov
    # data = data.rename(columns={
    #     "Date": "Date",
    #     "Open": "Open",
    #     "High": "High",
    #     "Low": "Low",
    #     "Close": "Close",
    #     "Adj Close": "Adj Close",
    #     "Volume": "Volume"
    # })

    # Ukladanie dát do CSV súboru
    output_directory = f"Data-{directory_name}/"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    output_filename = os.path.join(output_directory, f"{ticker_symbol}.csv")
    data.to_csv(output_filename, index=False, header=True)

    # Odstránenie druhého riadku zo súboru
    with open(output_filename, 'r') as file:
        lines = file.readlines()

    # Zapíše späť všetko okrem druhého riadku
    with open(output_filename, 'w') as file:
        file.writelines(lines[:1] + lines[2:])

    print(f"Dáta boli uložené do súboru {output_filename}.")
