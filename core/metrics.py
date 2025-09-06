import numpy as np, pandas as pd  # 引入依赖库

MINS_PER_YEAR = 525600  # 1-min bars

# 定义函数 to_returns，实现具体功能逻辑
def to_returns(nav: pd.Series) -> pd.Series:
    return nav.pct_change().fillna(0.0)  # 返回结果

# 定义函数 sharpe，实现具体功能逻辑
def sharpe(nav: pd.Series, rf: float = 0.0, freq_per_year: int = MINS_PER_YEAR) -> float:  # 变量赋值
    r = to_returns(nav)  # 变量赋值
    if r.std() == 0:  # 条件判断
        return 0.0  # 返回结果
    return (r.mean() - rf/freq_per_year) / (r.std() + 1e-12) * np.sqrt(freq_per_year)  # 返回结果

# 定义函数 max_drawdown，实现具体功能逻辑
def max_drawdown(nav: pd.Series) -> float:
    cummax = nav.cummax()  # 变量赋值
    dd = nav / cummax - 1.0  # 变量赋值
    return dd.min()  # 返回结果

# 定义函数 drawdown_series，实现具体功能逻辑
def drawdown_series(nav: pd.Series) -> pd.Series:
    return nav / nav.cummax() - 1.0  # 返回结果
