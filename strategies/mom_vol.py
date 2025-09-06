import pandas as pd  # 引入依赖库
from core.strategy_base import BaseStrategy, StrategyParam  # 引入依赖库

# 定义类 MomentumVol，用于封装相关逻辑或功能模块
class MomentumVol(BaseStrategy):
    name, version = "MomentumVol", "1.0"  # 变量赋值
# 定义函数 parameters，实现具体功能逻辑
    def parameters(self):
        return {  # 返回结果
            "lookback": StrategyParam("lookback","int",60,1440),
            "vol_window": StrategyParam("vol_window","int",30,600)  # 函数调用
        }
# 定义函数 prepare，实现具体功能逻辑
    def prepare(self, data, meta):
        close = data["close"].unstack()  # 变量赋值
        mom = close.pct_change(meta.get("lookback",240))  # 变量赋值
        vol = close.pct_change().rolling(meta.get("vol_window",120)).std()  # 变量赋值
        self.rank_mom = mom.rank(axis=1,ascending=False)  # 变量赋值
        self.rank_vol = vol.rank(axis=1,ascending=True)  # 变量赋值
        self.score = self.rank_mom + self.rank_vol  # 变量赋值
# 定义函数 generate_signals，实现具体功能逻辑
    def generate_signals(self, bar, state):
        dt = bar.index.get_level_values(0)[0]  # 变量赋值
        if dt not in self.score.index: return bar["close"].copy()*0.0  # 条件判断
        score = self.score.loc[dt]  # 变量赋值
        sel = score.nsmallest(1).index.tolist()  # 变量赋值
        tw = bar.index.get_level_values(1).to_series().apply(lambda x: 1.0 if x in sel else 0.0)  # 变量赋值
        return tw.to_frame("target_weight")  # 返回结果
