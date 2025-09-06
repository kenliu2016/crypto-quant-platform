import uuid, json, yaml  # 引入依赖库
from core.backtester import Backtester  # 引入依赖库
from data_io.db import Session  # 引入依赖库
from data_io.schemas import Run, Metrics, Reports, EquityCurve  # 引入依赖库

# 定义函数 run_backtest，实现具体功能逻辑
def run_backtest(config: dict) -> str:
    run_id = str(uuid.uuid4())  # 变量赋值
    bt = Backtester(config)  # 变量赋值
    result = bt.run()  # 变量赋值

    with Session() as s:
        s.add(Run(run_id=run_id, run_type="backtest", strategy_id=config.get("strategy_id",0),  # 变量赋值
                  config=config, code_version="v1", status="done"))  # 变量赋值
        for k, v in result.metrics.items():  # 循环遍历
            s.add(Metrics(run_id=run_id, metric_name=k, metric_value=float(v)))  # 变量赋值
        eq = result.equity_df.reset_index()  # 变量赋值
        for r in eq.itertuples(index=False):  # 变量赋值
            s.add(EquityCurve(run_id=run_id, datetime=r.datetime, nav=float(r.nav), drawdown=float(getattr(r, "drawdown", 0.0))))  # 变量赋值
        s.add(Reports(run_id=run_id, report_path="#", artifact_paths={}))
        s.commit()  # 函数调用
    return run_id  # 返回结果
