import pandas as pd, numpy as np  # 引入依赖库
from core.strategy_base import BaseStrategy, StrategyParam  # 引入依赖库

# 定义类 PairsCointegration，用于封装相关逻辑或功能模块
class PairsCointegration(BaseStrategy):
    name, version = "PairsCI", "1.0"  # 变量赋值
# 定义函数 parameters，实现具体功能逻辑
    def parameters(self):
        return {  # 返回结果
            "pair_a": StrategyParam("pair_a","cat", choices=[]),  # 变量赋值
            "pair_b": StrategyParam("pair_b","cat", choices=[]),  # 变量赋值
            "lookback": StrategyParam("lookback","int", 240, 10080),
            "z_entry": StrategyParam("z_entry","float", 1.0, 3.0),
            "z_exit": StrategyParam("z_exit","float", 0.2, 1.5)  # 函数调用
        }
# 定义函数 prepare，实现具体功能逻辑
    def prepare(self, data, meta):
        close = data["close"].unstack()  # 变量赋值
        self.close = close  # 变量赋值
        self.codes = close.columns.tolist()  # 变量赋值
# 定义函数 generate_signals，实现具体功能逻辑
    def generate_signals(self, bar, state):
        a = state.get("pair_a"); b = state.get("pair_b")  # 变量赋值
        lb = int(state.get("lookback", 1440))  # 变量赋值
        z_in = float(state.get("z_entry", 2.0)); z_out = float(state.get("z_exit", 0.5))  # 变量赋值
        dt = bar.index.get_level_values(0)[0]  # 变量赋值
        if a not in self.codes or b not in self.codes or dt not in self.close.index:  # 条件判断
            return pd.Series(0.0, index=bar.index.get_level_values(1)).to_frame("target_weight")  # 变量赋值
        df = self.close[[a,b]].loc[:dt].tail(lb+1)  # 变量赋值
        if df.shape[0] < lb//2:  # 条件判断
            return pd.Series(0.0, index=bar.index.get_level_values(1)).to_frame("target_weight")  # 变量赋值
        x = df[a]; y = df[b]  # 变量赋值
        # hedge ratio beta = cov(x,y)/var(y)
        beta = y.cov(x) / (y.var() + 1e-12)  # 变量赋值
        spread = x - beta*y  # 变量赋值
        z = (spread - spread.mean()) / (spread.std() + 1e-12)  # 变量赋值
        z_now = z.iloc[-1]  # 变量赋值
        # positions: when z > z_entry -> short x long y*beta ; when z < -z_entry -> long x short y*beta
        tw = pd.Series(0.0, index=bar.index.get_level_values(1).unique())  # 变量赋值
        if z_now > z_in:  # 条件判断
            tw.loc[a] = -0.5  # 变量赋值
            tw.loc[b] = +0.5  # 变量赋值
        elif z_now < -z_in:
            tw.loc[a] = +0.5  # 变量赋值
            tw.loc[b] = -0.5  # 变量赋值
        # exit if |z| < z_exit -> flat handled by no new entry; decay exposure
        if abs(z_now) < z_out:  # 条件判断
            tw.loc[a] = 0.0; tw.loc[b] = 0.0  # 变量赋值
        # normalize
        s = tw.abs().sum() or 1.0  # 变量赋值
        tw = tw / s  # 变量赋值
        return tw.reindex(bar.index.get_level_values(1)).to_frame("target_weight")  # 返回结果
