from dataclasses import dataclass  # 引入依赖库
from typing import Dict, Any  # 引入依赖库
import pandas as pd  # 引入依赖库
from .metrics import sharpe, drawdown_series  # 引入依赖库

@dataclass
# 定义类 PortfolioState，用于封装相关逻辑或功能模块
class PortfolioState:
    cash: float = 100000.0  # 变量赋值
    positions: dict = None  # code -> qty
    avg_price: dict = None  # code -> avg price
    equity: float = 100000.0  # 变量赋值

# 定义类 PortfolioTracker，用于封装相关逻辑或功能模块
class PortfolioTracker:
# 定义函数 __init__，实现具体功能逻辑
    def __init__(self, init_cash: float = 100000.0):  # 变量赋值
        self.state = PortfolioState(cash=init_cash, positions={}, avg_price={}, equity=init_cash)  # 变量赋值
        self.nav = []  # (datetime, nav)
        self.dd = []  # 变量赋值

# 定义函数 mark_to_market，实现具体功能逻辑
    def mark_to_market(self, dt, prices: pd.Series):
        equity = self.state.cash  # 变量赋值
        for code, qty in self.state.positions.items():  # 循环遍历
            equity += qty * float(prices.get(code, self.state.avg_price.get(code, 0.0)))  # 变量赋值
        self.state.equity = equity  # 变量赋值
        self.nav.append((dt, equity))  # 函数调用

# 定义函数 snapshot_drawdown，实现具体功能逻辑
    def snapshot_drawdown(self):
        import pandas as pd  # 引入依赖库
        nav = pd.Series([v for _, v in self.nav])  # 变量赋值
        dd = drawdown_series(nav)  # 变量赋值
        self.dd.append(dd.iloc[-1] if not dd.empty else 0.0)  # 函数调用

# 定义函数 metrics，实现具体功能逻辑
    def metrics(self):
        import pandas as pd  # 引入依赖库
        nav = pd.Series([v for _, v in self.nav])  # 变量赋值
        if nav.empty: return {"sharpe": 0.0, "max_drawdown": 0.0}  # 条件判断
        return {  # 返回结果
            "sharpe": sharpe(nav),
            "max_drawdown": float(drawdown_series(nav).min())  # 函数调用
        }
