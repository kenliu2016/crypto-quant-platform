import pandas as pd  # 引入依赖库
from core.strategy_base import BaseStrategy, StrategyParam  # 引入依赖库

# 定义类 SMACrossover，用于封装相关逻辑或功能模块
class SMACrossover(BaseStrategy):
    name, version = "SMACross", "1.0"  # 变量赋值
# 定义函数 parameters，实现具体功能逻辑
    def parameters(self):
        return {  # 返回结果
            "fast": StrategyParam("fast", "int", 5, 50),
            "slow": StrategyParam("slow", "int", 20, 200),
            "vol_target": StrategyParam("vol_target", "float", 0.05, 1.0),  # annualized target vol
            "ewm_halflife": StrategyParam("ewm_halflife","int", 10, 200)  # 函数调用
        }
# 定义函数 prepare，实现具体功能逻辑
    def prepare(self, data, meta):
        g = data.groupby(level=1)["close"]  # 变量赋值
        self.ma_fast = g.rolling(meta.get("fast", 10)).mean().droplevel(0)  # 变量赋值
        self.ma_slow = g.rolling(meta.get("slow", 50)).mean().droplevel(0)  # 变量赋值
        # realized vol (EWMA of returns)
        px = g.droplevel(0)  # 变量赋值
        rets = px.groupby(level=0, group_keys=False).apply(lambda s: s).unstack()  # pivot to compute returns per code
        rets = rets.pct_change().fillna(0.0)  # 变量赋值
        vol = rets.ewm(halflife=meta.get("ewm_halflife", 60), min_periods=5).std()  # 变量赋值
        self.vol = vol.stack()  # 变量赋值
# 定义函数 generate_signals，实现具体功能逻辑
    def generate_signals(self, bar, state):
        cross = (self.ma_fast.loc[bar.index] > self.ma_slow.loc[bar.index]).astype(int)*2-1  # -1/1
        # volatility targeting into target_weight
        vol = self.vol.reindex(bar.index).fillna(method="ffill").fillna(0.0)  # 变量赋值
        ann_factor = 525600**0.5  # sqrt per-minute to annualized std factor (approx)
        # avoid divide by zero
        inv_vol = 1.0 / (vol.replace(0, pd.NA).fillna(vol.mean()))   # 变量赋值
        tw = cross * inv_vol  # 变量赋值
        tw = tw / tw.abs().groupby(level=0).sum().replace(0, 1.0)  # normalize per timestamp
        return tw.to_frame("target_weight")  # 返回结果
