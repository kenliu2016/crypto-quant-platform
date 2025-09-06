import pandas as pd  # 引入依赖库
from core.strategy_base import BaseStrategy, StrategyParam  # 引入依赖库

# 定义类 MeanReversion，用于封装相关逻辑或功能模块
class MeanReversion(BaseStrategy):
    name, version = "MeanReversion", "1.0"  # 变量赋值
# 定义函数 parameters，实现具体功能逻辑
    def parameters(self):
        return {  # 返回结果
            "lookback": StrategyParam("lookback","int",5,60),
            "entry_z": StrategyParam("entry_z","float",1.0,3.0),
            "exit_z": StrategyParam("exit_z","float",0.1,1.5),
        }
# 定义函数 prepare，实现具体功能逻辑
    def prepare(self, data, meta):
        g = data.groupby(level=1)["close"]  # 变量赋值
        self.ma = g.rolling(meta.get("lookback",20)).mean().droplevel(0)  # 变量赋值
        self.sd = g.rolling(meta.get("lookback",20)).std().droplevel(0)  # 变量赋值
# 定义函数 generate_signals，实现具体功能逻辑
    def generate_signals(self, bar, state):
        z = (bar["close"] - self.ma.loc[bar.index]) / (self.sd.loc[bar.index] + 1e-9)  # 变量赋值
        sig = (z < -state.get("entry_z",2)).astype(int) - (z > state.get("entry_z",2)).astype(int)  # 变量赋值
        return sig.to_frame("signal")  # 返回结果
