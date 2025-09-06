"""
测试脚本：从数据库加载策略 → 运行回测 → 保存结果
运行方式:
    python apps/test_run.py --strategy ts_momentum --codes BTCUSDT ETHUSDT --start 2024-01-01 --end 2024-01-15
"""
import sys
import os
# ========= 自动加入项目根目录到 sys.path =========
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))      # apps/
ROOT_DIR = os.path.dirname(CURRENT_DIR)                       # crypto-quant-platform/
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)
import argparse
from core.db import get_connection, get_engine
import uuid
import datetime
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text


# ========= 导入项目模块 =========
from core.backtester import Backtester
import sys
import os

# 确保项目根目录在sys.path中
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(CURRENT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from core.db import get_engine
from data_io.schemas import Run, Metrics, EquityCurve
from sqlalchemy.orm import sessionmaker

# 创建session
engine = get_engine()
Session = sessionmaker(bind=engine)


def load_strategy_from_db(name: str, session):
    """从数据库加载策略参数"""
    sql = text("SELECT id, name, params FROM strategies WHERE name = :name LIMIT 1")
    row = session.execute(sql, {"name": name}).fetchone()
    if not row:
        raise ValueError(f"策略 {name} 未注册，请先执行 db/init_strategies.sql")
    return dict(row._mapping)


def generate_dummy_data(codes, start, end):
    """生成简单的测试数据 (分钟K线，假数据)"""
    idx = pd.date_range(start=start, end=end, freq="1min")
    data = []
    for code in codes:
        price = 100 + np.cumsum(np.random.randn(len(idx)))  # 随机游走
        df = pd.DataFrame({
            "datetime": idx,
            "code": code,
            "open": price,
            "high": price * (1 + 0.001),
            "low": price * (1 - 0.001),
            "close": price,
            "volume": np.random.randint(100, 1000, size=len(idx))
        })
        data.append(df)
    return pd.concat(data).set_index(["datetime", "code"]).sort_index()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", type=str, required=True, help="策略名称 (如 ts_momentum)")
    parser.add_argument("--codes", nargs="+", required=True, help="标的代码 (如 BTCUSDT ETHUSDT)")
    parser.add_argument("--start", type=str, required=True, help="开始时间")
    parser.add_argument("--end", type=str, required=True, help="结束时间")
    args = parser.parse_args()

    run_id = str(uuid.uuid4())

    # 连接数据库
    engine = get_engine()
    session = Session()

    # 加载策略配置
    strategy = load_strategy_from_db(args.strategy, session)
    print(f"已加载策略: {strategy['name']} 参数: {strategy['params']}")

    # 构造回测配置
    cfg = {
        "strategy_id": strategy["id"],
        "params": strategy["params"],
        "codes": args.codes,
        "start": args.start,
        "end": args.end,
        "initial_capital": 100000,
        "slippage": 0.0005,
        "fee": 0.0005,
    }

    # 生成测试数据
    data = generate_dummy_data(args.codes, args.start, args.end)

    # 运行回测
    bt = Backtester(cfg, data)
    result = bt.run()

    # 保存运行结果
    with Session() as s:
        s.add(Run(
            run_id=run_id,
            run_type="backtest",
            strategy_id=strategy["id"],
            config=str(cfg),
            code_version="dev",
            started_at=datetime.datetime.now(),
            ended_at=datetime.datetime.now(),
            status="success"
        ))
        # 保存指标
        for k, v in result.metrics.items():
            s.add(Metrics(run_id=run_id, metric_name=k, metric_value=float(v)))
        # 保存净值曲线
        for t, nav, dd in result.equity_curve.itertuples():
            s.add(EquityCurve(run_id=run_id, datetime=t, nav=nav, drawdown=dd))
        s.commit()

    print(f"✅ 回测完成，运行ID: {run_id}")


if __name__ == "__main__":
    main()
