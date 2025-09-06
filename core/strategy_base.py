from dataclasses import dataclass  # 引入依赖库
from typing import Dict, Any, Optional  # 引入依赖库
import pandas as pd  # 引入依赖库

@dataclass
# 定义类 StrategyParam，用于封装相关逻辑或功能模块
class StrategyParam:
    name: str
    type: str  # int/float/cat/bool
    low: float | None = None  # 变量赋值
    high: float | None = None  # 变量赋值
    choices: list | None = None  # 变量赋值
    log: bool = False  # 变量赋值

# 定义类 BaseStrategy，用于封装相关逻辑或功能模块
class BaseStrategy:
    name: str = "Base"  # 变量赋值
    version: str = "0.1.0"  # 变量赋值

# 定义函数 parameters，实现具体功能逻辑
    def parameters(self) -> Dict[str, StrategyParam]:
        raise NotImplementedError

# 定义函数 prepare，实现具体功能逻辑
    def prepare(self, data: pd.DataFrame, meta: Dict[str, Any]) -> None:
        pass

# 定义函数 generate_signals，实现具体功能逻辑
    def generate_signals(self, bar: pd.DataFrame, state: Dict[str, Any]) -> pd.DataFrame:
        raise NotImplementedError

# 定义函数 on_fill，实现具体功能逻辑
    def on_fill(self, fill_event: Dict[str, Any], state: Dict[str, Any]) -> None:
        pass
