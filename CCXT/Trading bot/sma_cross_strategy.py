from datetime import datetime
import pytz


class SMACrossStrategy:
    def __init__(self):
        self.position = 0  # 0 = bez pozície, 1 = v pozícii
        self.stop_loss_price = None
        self.take_profit_price = None

    def execute(self, df, symbol, account_name, exchange, truncate_function, buy_with_coin, sell_coin):
        # Výpočet SMA
        df["SMA_fast"] = df["close"].rolling(window=9).mean()  # Rýchlejšia SMA
        df["SMA_slow"] = df["close"].rolling(window=24).mean()  # Pomalšia SMA

        # Získanie posledných hodnôt
        last_sma_fast = df["SMA_fast"].iloc[-1]
        last_sma_slow = df["SMA_slow"].iloc[-1]
        prev_sma_fast = df["SMA_fast"].iloc[-2]
        prev_sma_slow = df["SMA_slow"].iloc[-2]
        last_row = df.iloc[-1]

        # Získanie času
        utc_now = datetime.now(pytz.utc)
        local_timezone = pytz.timezone("Europe/Bratislava")
        local_time = utc_now.astimezone(local_timezone)

        if self.position == 0:
            # Získanie zostatku
            sub_account_money_balance = exchange.fetch_balance()['total'][buy_with_coin]
            if sub_account_money_balance >= 10 and self.position == 0:
                amount_to_buy = sub_account_money_balance / last_row["close"]
                adjusted_amount_to_buy = truncate_function(amount_to_buy, 8)
                print(f"    {account_name} Account balance: {sub_account_money_balance}{buy_with_coin}")
            else:
                adjusted_amount_to_buy = 0
                print(f"{account_name} Nedostatok peňazí na účte")

        if self.position == 1:
            amount_to_sell = exchange.fetch_balance()["total"][sell_coin]

        ticker = exchange.fetch_ticker(symbol)
        current_price = float(ticker['last'])

        stop_loss_percent = 0.45
        take_profit_percent = 0.70

        # Nákupná podmienka (zlatý kríž)
        if (self.position == 0 and
                prev_sma_fast <= prev_sma_slow and
                last_sma_fast > last_sma_slow and
                sub_account_money_balance > 10):

            buy_order = exchange.create_order(symbol, 'market', 'buy', adjusted_amount_to_buy)
            self.stop_loss_price = current_price * (1 - stop_loss_percent / 100)
            self.take_profit_price = current_price * (1 + take_profit_percent / 100)
            self.position = 1
            print(f"{account_name} Kúpené za cenu: {current_price}, Stop loss: {self.stop_loss_price}")
            print(f"{account_name} Čas: {local_time}")

        # Predajná podmienka (smrtiaci kríž alebo stop loss/take profit)
        if self.position == 1:
            if current_price <= self.stop_loss_price or current_price >= self.take_profit_price:
                sell_order = exchange.create_order(symbol, 'market', 'sell', amount_to_sell)
                self.position = 0
                self.stop_loss_price = None
                self.take_profit_price = None
                print(f"{account_name} Predané za cenu: {current_price}")
                print(f"{account_name} Čas: {local_time}")
            elif prev_sma_fast >= prev_sma_slow and last_sma_fast < last_sma_slow:
                sell_order = exchange.create_order(symbol, 'market', 'sell', amount_to_sell)
                self.position = 0
                self.stop_loss_price = None
                self.take_profit_price = None
                print(f"{account_name} Predané na základe SMA kríža za cenu: {current_price}")
                print(f"{account_name} Čas: {local_time}")

        # Výpisy
        if self.position == 0:
            print(f"{account_name} {local_time} Čakanie na nákup")
            print(f"    last_sma_fast: {last_sma_fast}, last_sma_slow: {last_sma_slow}")
        elif self.position == 1:
            print(f"{account_name} {local_time} Čakanie na predaj")
            print(f"    last_sma_fast: {last_sma_fast}, last_sma_slow: {last_sma_slow}")
