import numpy as np, pandas as pd  # 引入依赖库
from core.strategy_base import BaseStrategy, StrategyParam  # 引入依赖库

# 定义类 SimpleMaker，用于封装相关逻辑或功能模块
class SimpleMaker(BaseStrategy):
    name, version = "SimpleMaker", "1.0"  # 变量赋值
# 定义函数 parameters，实现具体功能逻辑
    def parameters(self):
        return {  # 返回结果
            "halflife_vol": StrategyParam("halflife_vol","int", 60, 1440),
            "inventory_cap": StrategyParam("inventory_cap","float", 0.02, 0.3),
            "kappa": StrategyParam("kappa","float", 0.1, 5.0),  # sensitivity to price move
        }
# 定义函数 prepare，实现具体功能逻辑
    def prepare(self, data, meta):
        close = data["close"].unstack()  # 变量赋值
        ret = close.pct_change().fillna(0.0)  # 变量赋值
        self.std = ret.ewm(halflife=meta.get("halflife_vol", 240), min_periods=5).std()  # 变量赋值
        self.mid = close  # 变量赋值
# 定义函数 generate_signals，实现具体功能逻辑
    def generate_signals(self, bar, state):
        dt = bar.index.get_level_values(0)[0]  # 变量赋值
        codes = bar.index.get_level_values(1)  # 变量赋值
        std = self.std.loc[dt].reindex(codes).fillna(self.std.median())  # 变量赋值
        inv_cap = float(state.get("inventory_cap", 0.1))  # 变量赋值
        kappa = float(state.get("kappa", 1.0))  # 变量赋值
        # Target inventory proportional to -zscore of last return (mean-reverting inventory)
        # Here we approximate with 0 target (flat) but small oscillation based on deviation from rolling median
        px = self.mid.loc[dt].reindex(codes)  # 变量赋值
        roll = self.mid.rolling(60).median().loc[dt].reindex(codes)  # 变量赋值
        z = (px - roll) / (std.replace(0, np.nan))  # 变量赋值
        tw = (-kappa * z).clip(-inv_cap, inv_cap)  # 变量赋值
        # normalize across codes to keep total abs exposure <= inv_cap
        scale = tw.abs().sum() or 1.0  # 变量赋值
        if scale > inv_cap:  # 条件判断
            tw = tw * (inv_cap / scale)  # 变量赋值
        return tw.to_frame("target_weight")  # 返回结果
