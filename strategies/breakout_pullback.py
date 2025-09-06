import pandas as pd  # 引入依赖库
from core.strategy_base import BaseStrategy, StrategyParam  # 引入依赖库

# 定义类 BreakoutPullback，用于封装相关逻辑或功能模块
class BreakoutPullback(BaseStrategy):
    name, version = "BreakoutPullback", "1.0"  # 变量赋值
# 定义函数 parameters，实现具体功能逻辑
    def parameters(self):
        return {  # 返回结果
            "lookback": StrategyParam("lookback","int", 100, 1000),
            "pullback": StrategyParam("pullback","float", 0.2, 0.8),
        }
# 定义函数 prepare，实现具体功能逻辑
    def prepare(self, data, meta):
        g = data.groupby(level=1)  # 变量赋值
        self.high = g["high"].rolling(meta.get("lookback", 300)).max().droplevel(0)  # 变量赋值
        self.low = g["low"].rolling(meta.get("lookback", 300)).min().droplevel(0)  # 变量赋值
# 定义函数 generate_signals，实现具体功能逻辑
    def generate_signals(self, bar, state):
        hb = self.high.loc[bar.index]  # 变量赋值
        lb = self.low.loc[bar.index]  # 变量赋值
        price = bar["close"]  # 变量赋值
        mid = (hb + lb) / 2.0  # 变量赋值
        pull = state.get("pullback", 0.5)  # 变量赋值
        up_zone = lb + (hb - lb) * pull  # 变量赋值
        sig = (price > up_zone).astype(int)*2 - 1  # 变量赋值
        return sig.to_frame("signal")  # 返回结果
