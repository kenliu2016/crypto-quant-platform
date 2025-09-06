import pandas as pd, numpy as np, statsmodels.api as sm  # 引入依赖库
from core.strategy_base import BaseStrategy, StrategyParam  # 引入依赖库

# 定义类 PairsTrading，用于封装相关逻辑或功能模块
class PairsTrading(BaseStrategy):
    name, version = "PairsTrading", "1.0"  # 变量赋值
# 定义函数 parameters，实现具体功能逻辑
    def parameters(self):
        return {  # 返回结果
            "lookback": StrategyParam("lookback","int",100,2000),
            "entry_z": StrategyParam("entry_z","float",1.0,3.0),
            "exit_z": StrategyParam("exit_z","float",0.2,1.0)  # 函数调用
        }
# 定义函数 prepare，实现具体功能逻辑
    def prepare(self, data, meta):
        close = data["close"].unstack().dropna(axis=1, how="any")  # 变量赋值
        if close.shape[1]<2: return  # 条件判断
        y,x = close.iloc[:,0], close.iloc[:,1]  # 变量赋值
        x=sm.add_constant(x)  # 变量赋值
        model = sm.OLS(y,x).fit()  # 变量赋值
        spread = y - model.predict(x)  # 变量赋值
        z = (spread-spread.mean())/spread.std()  # 变量赋值
        self.z = z  # 变量赋值
# 定义函数 generate_signals，实现具体功能逻辑
    def generate_signals(self, bar, state):
        dt = bar.index.get_level_values(0)[0]  # 变量赋值
        if dt not in self.z.index: return bar["close"].copy()*0.0  # 条件判断
        z = self.z.loc[dt]  # 变量赋值
        entry = state.get("entry_z",2.0); exit = state.get("exit_z",0.5)  # 变量赋值
        sig = 0  # 变量赋值
        if z>entry: sig=-1  # 变量赋值
        elif z<-entry: sig=1  # 变量赋值
        elif abs(z)<exit: sig=0  # 变量赋值
        return pd.Series(sig,index=bar.index).to_frame("signal")  # 变量赋值
