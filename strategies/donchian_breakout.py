import pandas as pd  # 引入依赖库
from core.strategy_base import BaseStrategy, StrategyParam  # 引入依赖库

# 定义类 DonchianBreakout，用于封装相关逻辑或功能模块
class DonchianBreakout(BaseStrategy):
    name, version = "Donchian", "1.0"  # 变量赋值
# 定义函数 parameters，实现具体功能逻辑
    def parameters(self):
        return {  # 返回结果
            "window": StrategyParam("window","int", 20, 200),
            "stop_atr": StrategyParam("stop_atr","float", 1.0, 5.0),
            "atr_window": StrategyParam("atr_window","int", 7, 50)  # 函数调用
        }
# 定义函数 prepare，实现具体功能逻辑
    def prepare(self, data, meta):
        g_high = data.groupby(level=1)["high"]  # 变量赋值
        g_low = data.groupby(level=1)["low"]  # 变量赋值
        g_close = data.groupby(level=1)["close"]  # 变量赋值
        w = meta.get("window", 55)  # 变量赋值
        self.dc_high = g_high.rolling(w).max().droplevel(0)  # 变量赋值
        self.dc_low = g_low.rolling(w).min().droplevel(0)  # 变量赋值
        # ATR
        high = g_high.droplevel(0); low = g_low.droplevel(0); close = g_close.droplevel(0)  # 变量赋值
        prev_close = close.groupby(level=1).shift(1)  # 变量赋值
        tr = (high - low).abs().combine((high - prev_close).abs(), max).combine((low - prev_close).abs(), max)  # 变量赋值
        self.atr = tr.groupby(level=1).rolling(meta.get("atr_window",14)).mean().droplevel(0)  # 变量赋值
# 定义函数 generate_signals，实现具体功能逻辑
    def generate_signals(self, bar, state):
        price = bar["close"]  # 变量赋值
        up = (price >= self.dc_high.loc[bar.index]).astype(int)  # 变量赋值
        dn = (price <= self.dc_low.loc[bar.index]).astype(int)  # 变量赋值
        sig = up - dn  # 1 long, -1 short
        return sig.to_frame("signal")  # 返回结果
