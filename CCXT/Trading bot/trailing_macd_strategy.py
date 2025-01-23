class MACDStrategyTrailingSL:
    def __init__(self):
        self.stop_price = None
        self.macd_strategy_position = 0

    def execute(self, df, symbol, account_name, exchange, truncate_function, calculate_macd):
        calculate_macd(df)

        last_macd_line = df["MACD"].iloc[-1]
        last_signal_line = df["signal_line"].iloc[-1]
        last_row = df.iloc[-1]
        prev_macd_line = df["MACD"].iloc[-2]
        prev_signal_line = df["signal_line"].iloc[-2]
        third_macd_line = df["MACD"].iloc[-3]
        third_signal_line = df["signal_line"].iloc[-3]

        sub_account_money_balance = exchange.fetch_balance()['total']['EUR']
        if sub_account_money_balance >= 10:
            amount_to_buy = sub_account_money_balance / last_row["close"]
            adjusted_amount_to_buy = truncate_function(amount_to_buy)
        else:
            adjusted_amount_to_buy = 0
            print("Nedostatok peňazí na účte")

        amount_to_sell = exchange.fetch_balance()["total"]["LTC"]

        ticker = exchange.fetch_ticker(symbol)
        current_price = float(ticker['last'])

        trailing_percent = 0.55

        # Kúpna podmienka
        if (self.macd_strategy_position == 0 and
                last_macd_line > last_signal_line and
                prev_macd_line <= prev_signal_line and
                third_macd_line < third_signal_line and
                sub_account_money_balance > 10):

            buy_order = exchange.create_order(symbol, 'market', 'buy', adjusted_amount_to_buy, last_row["close"])
            self.stop_price = current_price * (1 - trailing_percent / 100)
            self.macd_strategy_position = 1
            print(f"Kúpené za cenu: {current_price}, Stop loss: {self.stop_price}")

        # Trailing stop loss aktualizácia
        if self.macd_strategy_position == 1:
            if self.stop_price is not None:
                if current_price > self.stop_price / (1 - trailing_percent / 100):
                    self.stop_price = current_price * (1 - trailing_percent / 100)
                    print(f"Stop loss posunutý na: {self.stop_price}")

        # Predajná podmienka
        if self.macd_strategy_position == 1 and current_price <= self.stop_price and amount_to_sell > 0:
            sell_order = exchange.create_order(symbol, 'market', 'sell', amount_to_sell, last_row["close"])
            self.macd_strategy_position = 0
            self.stop_price = None
            print(f"Predané za cenu: {current_price}")
