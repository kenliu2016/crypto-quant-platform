import pandas as pd, numpy as np  # 引入依赖库
from core.strategy_base import BaseStrategy, StrategyParam  # 引入依赖库

# 定义类 MomoLowVol，用于封装相关逻辑或功能模块
class MomoLowVol(BaseStrategy):
    name, version = "MomoLowVol", "1.0"  # 变量赋值
# 定义函数 parameters，实现具体功能逻辑
    def parameters(self):
        return {  # 返回结果
            "momo_lb": StrategyParam("momo_lb","int", 240, 10080),
            "vol_hl": StrategyParam("vol_hl","int", 60, 1440),
            "long_n": StrategyParam("long_n","int", 1, 10),
            "short_n": StrategyParam("short_n","int", 0, 10),
            "combo_alpha": StrategyParam("combo_alpha","float", 0.2, 0.8),  # blend weight for momentum vs low-vol
        }
# 定义函数 prepare，实现具体功能逻辑
    def prepare(self, data, meta):
        close = data["close"].unstack()  # 变量赋值
        # momentum: past lb return
        lb = meta.get("momo_lb", 1440)  # 变量赋值
        self.momo = close.pct_change(lb)  # 变量赋值
        # low-vol: negative of recent std (EWMA)
        vol = close.pct_change().ewm(halflife=meta.get("vol_hl", 240), min_periods=5).std()  # 变量赋值
        self.lowvol = -vol  # 变量赋值
        self.codes = close.columns  # 变量赋值
# 定义函数 generate_signals，实现具体功能逻辑
    def generate_signals(self, bar, state):
        dt = bar.index.get_level_values(0)[0]  # 变量赋值
        if dt not in self.momo.index:  # 条件判断
            return pd.Series(0.0, index=bar.index.get_level_values(1)).to_frame("target_weight")  # 变量赋值
        alpha = float(state.get("combo_alpha", 0.5))  # 变量赋值
        score = alpha * self.momo.loc[dt].reindex(self.codes) + (1-alpha) * self.lowvol.loc[dt].reindex(self.codes)  # 变量赋值
        score = score.dropna()  # 变量赋值
        long_n = int(state.get("long_n", 2)); short_n = int(state.get("short_n", 0))  # 变量赋值
        tw = pd.Series(0.0, index=self.codes)  # 变量赋值
        if long_n>0:  # 条件判断
            L = score.nlargest(long_n).index  # 变量赋值
            tw.loc[L] = 1.0 / max(long_n,1)  # 变量赋值
        if short_n>0:  # 条件判断
            S = score.nsmallest(short_n).index  # 变量赋值
            tw.loc[S] = -1.0 / max(short_n,1)  # 变量赋值
        # normalize
        s = tw.abs().sum() or 1.0  # 变量赋值
        tw = tw / s  # 变量赋值
        return tw.reindex(bar.index.get_level_values(1)).to_frame("target_weight")  # 返回结果
