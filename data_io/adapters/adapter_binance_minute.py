import pandas as pd  # 引入依赖库

# 定义类 BinanceMinuteAdapter，用于封装相关逻辑或功能模块
class BinanceMinuteAdapter:
# 定义函数 __init__，实现具体功能逻辑
    def __init__(self, engine):
        self.engine = engine  # 变量赋值

# 定义函数 load，实现具体功能逻辑
    def load(self, codes, start, end, fields):
        # Example assumes a table minutes(code, datetime, open, high, low, close, volume)
        q = """  # 变量赋值
        SELECT datetime, code, open, high, low, close, volume
        FROM minutes
        WHERE code = ANY(:codes) AND datetime BETWEEN :start AND :end  # 变量赋值
        ORDER BY datetime
        """
        df = pd.read_sql(q, self.engine, params={"codes": codes, "start": start, "end": end}, parse_dates=["datetime"])  # 变量赋值
        return df.set_index(["datetime","code"]).sort_index()  # 返回结果
