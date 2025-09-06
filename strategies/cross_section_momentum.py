import pandas as pd  # 引入依赖库
from core.strategy_base import BaseStrategy, StrategyParam  # 引入依赖库

# 定义类 CrossSectionMomentum，用于封装相关逻辑或功能模块
class CrossSectionMomentum(BaseStrategy):
    name, version = "XSecMomentum", "1.0"  # 变量赋值
# 定义函数 parameters，实现具体功能逻辑
    def parameters(self):
        return {  # 返回结果
            "lookback": StrategyParam("lookback","int", 60, 1440),  # minutes
            "topn": StrategyParam("topn","int", 1, 10),
            "bottomn": StrategyParam("bottomn","int", 0, 10),
        }
# 定义函数 prepare，实现具体功能逻辑
    def prepare(self, data, meta):
        close = data["close"].unstack()  # rows dt, cols code
        ret = close.pct_change(meta.get("lookback", 240))  # 变量赋值
        self.rank = ret.rank(axis=1, ascending=False, method="first")  # 变量赋值
# 定义函数 generate_signals，实现具体功能逻辑
    def generate_signals(self, bar, state):
        # Rebuild ranks for the current timestamp subset
        dt = bar.index.get_level_values(0)[0]  # 变量赋值
        if dt not in self.rank.index:  # 条件判断
            return pd.Series(0, index=bar.index).to_frame("target_weight")  # 变量赋值
        r = self.rank.loc[dt].dropna()  # 变量赋值
        topn = int(state.get("topn", 2)); bottomn = int(state.get("bottomn", 0))  # 变量赋值
        longs = r.nsmallest(topn).index.tolist()  # 变量赋值
        shorts = r.nlargest(bottomn).index.tolist() if bottomn>0 else []  # 变量赋值
        tw = pd.Series(0.0, index=bar.index.get_level_values(1).unique())  # 变量赋值
        if topn>0: tw.loc[longs] = 1.0 / max(len(longs),1)  # 变量赋值
        if bottomn>0: tw.loc[shorts] = -1.0 / max(len(shorts),1)  # 变量赋值
        # normalize total absolute to 1
        scale = tw.abs().sum() or 1.0  # 变量赋值
        tw = tw / scale  # 变量赋值
        return tw.reindex(bar.index.get_level_values(1)).to_frame("target_weight")  # 返回结果
