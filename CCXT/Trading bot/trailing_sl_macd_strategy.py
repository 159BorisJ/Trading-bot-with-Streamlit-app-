from datetime import datetime
import pytz


class TrailingSLMACDStrategy:
    def __init__(self, decimal_places):
        self.stop_loss_price = None
        self.strategy_position = 0
        self.decimal_places = decimal_places

    def execute(self, df, symbol, account_name, exchange, truncate_function,
                calculate_macd, buy_with_coin, sell_coin):

        calculate_macd(df)

        # Získanie aktuálneho UTC času
        utc_now = datetime.now(pytz.utc)

        # Konverzia na časovú zónu Europe/Bratislava
        local_timezone = pytz.timezone("Europe/Bratislava")
        local_time = utc_now.astimezone(local_timezone)

        df["long_ema"] = df["close"].ewm(span=200, adjust=False).mean().round(2)
        long_ema = df["long_ema"].iloc[-1]

        last_macd_line = df["MACD"].iloc[-1]
        last_signal_line = df["signal_line"].iloc[-1]
        prev_macd_line = df["MACD"].iloc[-2]
        prev_signal_line = df["signal_line"].iloc[-2]
        third_macd_line = df["MACD"].iloc[-3]
        third_signal_line = df["signal_line"].iloc[-3]

        last_row = df.iloc[-1]

        if self.strategy_position == 0:
            sub_account_money_balance = exchange.fetch_balance()['total'][buy_with_coin]
            if sub_account_money_balance >= 10 and self.strategy_position == 0:
                amount_to_buy = sub_account_money_balance / last_row["close"]
                adjusted_amount_to_buy = truncate_function(amount_to_buy, self.decimal_places)
                print(f"    {account_name} Account balance: {sub_account_money_balance}{buy_with_coin}")
            else:
                adjusted_amount_to_buy = 0
                print(f"{account_name} Nedostatok peňazí na účte")

        if self.strategy_position == 1:
            amount_to_sell = exchange.fetch_balance()["total"][sell_coin]

        ticker = exchange.fetch_ticker(symbol)
        current_price = float(ticker['last'])

        trailing_percent = 1

        # Kúpna podmienka
        if (self.strategy_position == 0 and
                last_macd_line > last_signal_line and
                prev_macd_line <= prev_signal_line and
                third_macd_line < third_signal_line and
                last_macd_line < 0 and
                last_signal_line < 0 and
                last_row["close"] > long_ema and
                sub_account_money_balance > 10):

            buy_order = exchange.create_order(symbol, 'market', 'buy', adjusted_amount_to_buy)
            self.stop_loss_price = current_price * (1 - trailing_percent / 100)
            self.strategy_position = 1
            print("**********")
            print(f"{account_name} Kúpené za cenu: {current_price}, Stop loss: {self.stop_loss_price}")
            print(f"{account_name} Čas: {local_time}")
            print("**********")

        # Trailing stop loss aktualizácia
        if self.strategy_position == 1:
            if self.stop_loss_price is not None:
                if current_price > self.stop_loss_price / (1 - trailing_percent / 100):
                    self.stop_loss_price = current_price * (1 - trailing_percent / 100)
                    print(f"Stop loss posunutý na: {self.stop_loss_price}")

        # Predajná podmienka
        if self.strategy_position == 1 and current_price <= self.stop_loss_price and amount_to_sell > 0:
            sell_order = exchange.create_order(symbol, 'market', 'sell', amount_to_sell)
            self.strategy_position = 0
            self.stop_loss_price = None
            print("**********")
            print(f"{account_name} Predané za cenu: {current_price}")
            print(f"{account_name} Čas: {local_time}")
            print("**********")

        else:
            if self.strategy_position == 0:
                print(f"{account_name} {local_time} Čakanie na nákup")
                print(f"    last_macd_line: {last_macd_line}, last_signal_line: {last_signal_line}")
                print(f"    prev_macd_line: {prev_macd_line}, prev_signal_line: {prev_signal_line}")
                print(f"    third_macd_line: {third_macd_line}, third_signal_line: {third_signal_line}")
                print(f"    --last_row[close]: {last_row['close']}, long_ema: {long_ema}")

            elif self.strategy_position == 1:
                print(f"{account_name} {local_time} Čakanie na predaj")
                print(f"    last_macd_line: {last_macd_line}, last_signal_line: {last_signal_line}")
                print(f"    prev_macd_line: {prev_macd_line}, prev_signal_line: {prev_signal_line}")
                print(f"    third_macd_line: {third_macd_line}, third_signal_line: {third_signal_line}")
                print(f"    --last_row[close]: {last_row['close']}, long_ema: {long_ema}")


