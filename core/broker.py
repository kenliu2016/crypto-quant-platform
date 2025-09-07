import pandas as pd

class BrokerSim:
    def __init__(self, fee=0.001, slippage=0.0005, tracker=None):
        self.fee = fee
        self.slippage = slippage
        self.tracker = tracker
        self.trades = []

    def place_target_weights(self, dt, target_weights: pd.Series, prices: pd.Series):
        for code, weight in target_weights.items():
            price = prices.get(code)
            if price is None or pd.isna(price):
                continue  # ⚠️ 跳过缺失价格
            p = float(price)
            # 下单逻辑示例
            self.trades.append({
                "datetime": dt,
                "code": code,
                "price": p,
                "weight": weight
            })

    def get_trade_log(self):
        return self.trades
