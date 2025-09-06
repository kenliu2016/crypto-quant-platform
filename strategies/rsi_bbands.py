import pandas as pd, numpy as np  # 引入依赖库
from core.strategy_base import BaseStrategy, StrategyParam  # 引入依赖库

# 定义类 RSIBBands，用于封装相关逻辑或功能模块
class RSIBBands(BaseStrategy):
    name, version = "RSI_BBands", "1.0"  # 变量赋值
# 定义函数 parameters，实现具体功能逻辑
    def parameters(self):
        return {  # 返回结果
            "rsi_len": StrategyParam("rsi_len","int", 7, 30),
            "bb_len": StrategyParam("bb_len","int", 10, 60),
            "bb_k": StrategyParam("bb_k","float", 1.0, 3.0),
            "rsi_buy": StrategyParam("rsi_buy","int", 20, 45),
            "rsi_sell": StrategyParam("rsi_sell","int", 55, 80)  # 函数调用
        }
# 定义函数 prepare，实现具体功能逻辑
    def prepare(self, data, meta):
        g = data.groupby(level=1)["close"]  # 变量赋值
        # RSI
        c = g.droplevel(0)  # 变量赋值
        diff = c.groupby(level=1).diff()  # 变量赋值
        up = diff.clip(lower=0).groupby(level=1).rolling(meta.get("rsi_len",14)).mean().droplevel(0)  # 变量赋值
        dn = (-diff.clip(upper=0)).groupby(level=1).rolling(meta.get("rsi_len",14)).mean().droplevel(0)  # 变量赋值
        rs = up / (dn + 1e-12)  # 变量赋值
        self.rsi = 100 - 100 / (1 + rs)  # 变量赋值
        # BBands
        ma = g.rolling(meta.get("bb_len",20)).mean().droplevel(0)  # 变量赋值
        sd = g.rolling(meta.get("bb_len",20)).std().droplevel(0)  # 变量赋值
        k = meta.get("bb_k", 2.0)  # 变量赋值
        self.upper = ma + k*sd  # 变量赋值
        self.lower = ma - k*sd  # 变量赋值
# 定义函数 generate_signals，实现具体功能逻辑
    def generate_signals(self, bar, state):
        rsi_buy = state.get("rsi_buy", 30)  # 变量赋值
        rsi_sell = state.get("rsi_sell", 70)  # 变量赋值
        long_entry = (bar["close"] < self.lower.loc[bar.index]) & (self.rsi.loc[bar.index] < rsi_buy)  # 变量赋值
        long_exit = (bar["close"] >= self.upper.loc[bar.index]) | (self.rsi.loc[bar.index] > rsi_sell)  # 变量赋值
        sig = pd.Series(0, index=bar.index)  # 变量赋值
        sig[long_entry] = 1  # 变量赋值
        sig[long_exit] = 0  # 变量赋值
        return sig.to_frame("signal")  # 返回结果
