import yfinance as yf
import pandas as pd
import os

stocks = ["IBM", "GE", "KO", "MCD", "PG", "PEP", "JNJ", "XOM", "WMT"]

cryptos = ["BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "ADA-USD", "SOL-USD", "DOGE-USD", "DOT-USD", "LTC-USD", "AVAX-USD",
           "MATIC-USD", "UNI-USD", "ATOM-USD", "FTM-USD"]

comodities = cryptos

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


for c in comodities:
    ticker_symbol = c

    # Načítaj historické údaje
    data = yf.download(ticker_symbol, start=start_date, end=end_date)

    # Resetuj index, aby sme mali dátum ako stĺpec
    data.reset_index(inplace=True)
    data["Date"] = data["Date"].dt.strftime('%Y-%m-%d')

    # Uprav názvy stĺpcov, aby zodpovedali požadovanému formátu
    data = data.rename(columns={
        "Date": "Date",
        "Open": "Open",
        "High": "High",
        "Low": "Low",
        "Close": "Close",
        "Adj Close": "Adj Close",
        "Volume": "Volume"
    })

    # Ulož do CSV súboru
    output_directory = f"Data-{directory_name}/"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    output_filename = os.path.join(output_directory, f"{ticker_symbol}_{start_date}-{end_date}.csv")
    data.to_csv(output_filename, index=False, header=True)

    # Odstránenie druhého riadku zo súboru
    with open(output_filename, 'r') as file:
        lines = file.readlines()

    # Zapíše späť všetko okrem druhého riadku
    with open(output_filename, 'w') as file:
        file.writelines(lines[:1] + lines[2:])

    print(f"Dáta boli uložené do súboru {output_filename}.")
