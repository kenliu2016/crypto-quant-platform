import pandas as pd, numpy as np  # 引入依赖库
from core.strategy_base import BaseStrategy, StrategyParam  # 引入依赖库

# 定义类 VolTarget，用于封装相关逻辑或功能模块
class VolTarget(BaseStrategy):
    name, version = "VolTarget", "1.0"  # 变量赋值
# 定义函数 parameters，实现具体功能逻辑
    def parameters(self):
        return {  # 返回结果
            "halflife": StrategyParam("halflife","int", 30, 600),
            "ann_vol": StrategyParam("ann_vol","float", 0.1, 1.0),
        }
# 定义函数 prepare，实现具体功能逻辑
    def prepare(self, data, meta):
        close = data["close"].unstack()  # 变量赋值
        ret = close.pct_change().fillna(0.0)  # 变量赋值
        self.ewm_std = ret.ewm(halflife=meta.get("halflife", 120), min_periods=5).std()  # 变量赋值
# 定义函数 generate_signals，实现具体功能逻辑
    def generate_signals(self, bar, state):
        dt = bar.index.get_level_values(0)[0]  # 变量赋值
        if dt not in self.ewm_std.index:  # 条件判断
            return pd.Series(0.0, index=bar.index.get_level_values(1)).to_frame("target_weight")  # 变量赋值
        std = self.ewm_std.loc[dt]  # 变量赋值
        inv = 1.0 / std.replace(0, np.nan)  # 变量赋值
        inv = inv.fillna(inv[inv>0].median() or 1.0)  # 变量赋值
        tw = inv / inv.abs().sum()  # 变量赋值
        return tw.reindex(bar.index.get_level_values(1)).to_frame("target_weight")  # 返回结果
