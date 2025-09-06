import pandas as pd  # 引入依赖库
from core.strategy_base import BaseStrategy, StrategyParam  # 引入依赖库

# 定义类 TSMA，用于封装相关逻辑或功能模块
class TSMA(BaseStrategy):
    name, version = "TSMA", "1.0"  # 变量赋值
# 定义函数 parameters，实现具体功能逻辑
    def parameters(self):
        return {  # 返回结果
            "ma_fast": StrategyParam("ma_fast","int",3,50),
            "ma_slow": StrategyParam("ma_slow","int",10,200),
        }
# 定义函数 prepare，实现具体功能逻辑
    def prepare(self, data, meta):
        g = data.groupby(level=1)["close"]  # 变量赋值
        self.ma_f = g.rolling(meta.get("ma_fast",10)).mean().droplevel(0)  # 变量赋值
        self.ma_s = g.rolling(meta.get("ma_slow",50)).mean().droplevel(0)  # 变量赋值
# 定义函数 generate_signals，实现具体功能逻辑
    def generate_signals(self, bar, state):
        cross = (self.ma_f.loc[bar.index] > self.ma_s.loc[bar.index]).astype(int)*2-1  # 变量赋值
        return cross.to_frame("signal")  # 返回结果
