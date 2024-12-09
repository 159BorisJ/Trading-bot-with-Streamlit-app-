import pandas as pd

comodity_prices = pd.read_csv(f"Data-cryptos/BTC-USD.csv", parse_dates=True)

first_date = comodity_prices.iloc[0]["Date"]
last_date = comodity_prices.iloc[-1]["Date"]
period = f"{first_date}_{last_date}"

print(period)

