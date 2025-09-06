import pandas as pd  # 引入依赖库
from core.strategy_base import BaseStrategy, StrategyParam  # 引入依赖库

# 定义类 MACDTrend，用于封装相关逻辑或功能模块
class MACDTrend(BaseStrategy):
    name, version = "MACD", "1.0"  # 变量赋值
# 定义函数 parameters，实现具体功能逻辑
    def parameters(self):
        return {  # 返回结果
            "fast": StrategyParam("fast","int", 8, 20),
            "slow": StrategyParam("slow","int", 21, 40),
            "signal": StrategyParam("signal","int", 5, 15)  # 函数调用
        }
# 定义函数 prepare，实现具体功能逻辑
    def prepare(self, data, meta):
        g = data.groupby(level=1)["close"]  # 变量赋值
        c = g.droplevel(0)  # 变量赋值
        ema_fast = c.groupby(level=1).ewm(span=meta.get("fast",12), adjust=False).mean()  # 变量赋值
        ema_slow = c.groupby(level=1).ewm(span=meta.get("slow",26), adjust=False).mean()  # 变量赋值
        macd = ema_fast - ema_slow  # 变量赋值
        self.macd = macd  # 变量赋值
        self.sig = macd.groupby(level=1).ewm(span=meta.get("signal",9), adjust=False).mean()  # 变量赋值
# 定义函数 generate_signals，实现具体功能逻辑
    def generate_signals(self, bar, state):
        macd = self.macd.loc[bar.index]  # 变量赋值
        sigl = self.sig.loc[bar.index]  # 变量赋值
        sig = (macd > sigl).astype(int)*2 - 1  # 变量赋值
        return sig.to_frame("signal")  # 返回结果
