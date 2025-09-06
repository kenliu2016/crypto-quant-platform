import numpy as np, pandas as pd  # 引入依赖库
from core.strategy_base import BaseStrategy, StrategyParam  # 引入依赖库

# 定义类 GridTrading，用于封装相关逻辑或功能模块
class GridTrading(BaseStrategy):
    name, version = "GridTrading", "1.0"  # 变量赋值
# 定义函数 parameters，实现具体功能逻辑
    def parameters(self):
        return {  # 返回结果
            "center_lookback": StrategyParam("center_lookback","int", 1440, 20000),  # minutes
            "grid_step_bps": StrategyParam("grid_step_bps","float", 10.0, 200.0),    # step in basis points
            "max_abs_exposure": StrategyParam("max_abs_exposure","float", 0.1, 1.0), # max |weight|
        }
# 定义函数 prepare，实现具体功能逻辑
    def prepare(self, data, meta):
        g = data.groupby(level=1)["close"]  # 变量赋值
        c = g.droplevel(0)  # 变量赋值
        # dynamic center as rolling median to be robust
        self.center = g.rolling(meta.get("center_lookback", 10080)).median().droplevel(0)  # 变量赋值
# 定义函数 generate_signals，实现具体功能逻辑
    def generate_signals(self, bar, state):
        step_bps = float(state.get("grid_step_bps", 50.0))  # 变量赋值
        max_abs = float(state.get("max_abs_exposure", 0.5))  # 变量赋值
        p = bar["close"]  # 变量赋值
        cen = self.center.loc[bar.index].replace(0, np.nan).fillna(method="ffill")  # 变量赋值
        # log distance in bps
        dist = (np.log(p) - np.log(cen)) * 1e4  # bps
        steps = (-(dist / step_bps)).round()  # negative dist -> long
        tw = steps.clip(-max_abs*100, max_abs*100) / 100.0  # to weight
        # normalize per timestamp if needed
        s = tw.abs().groupby(level=0).sum().replace(0, 1.0)  # 变量赋值
        tw = tw / s  # 变量赋值
        return tw.to_frame("target_weight")  # 返回结果
