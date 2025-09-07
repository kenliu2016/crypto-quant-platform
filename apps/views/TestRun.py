import sys
import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

import streamlit as st
import pandas as pd
import datetime
import uuid
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

# ========= 导入项目模块 =========
from core.backtester import Backtester
from core.db import get_engine
from data_io.schemas import Run, Metrics, EquityCurve

engine = get_engine()
Session = sessionmaker(bind=engine)

def load_strategies():
    """加载数据库里所有已注册的策略"""
    with Session() as s:
        rows = s.execute(text("SELECT id, name, description FROM strategies ORDER BY id")).fetchall()
        return [dict(r._mapping) for r in rows]

# ============ 页面布局 ============
st.title("🚀 快速回测测试 (🧪 测试运行)")

# 策略选择
strategies = load_strategies()
strategy_options = {s["name"]: s for s in strategies}
strategy_name = st.selectbox("选择策略", list(strategy_options.keys()))

# 标的选择
codes = st.multiselect("选择交易标的", ["BTCUSDT","ETHUSDT","BNBUSDT"], default=["BTCUSDT"])

# 时间区间
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("开始日期", datetime.date(2024, 1, 1))
with col2:
    end_date = st.date_input("结束日期", datetime.date(2024, 12, 31))

# 执行按钮
if st.button("运行回测 🚦"):
    run_id = str(uuid.uuid4())
    st.write(f"运行ID: `{run_id}`")

    strategy = strategy_options[strategy_name]
    st.write(f"使用策略: **{strategy['name']}**")
    st.write(strategy["description"])

    # 构造配置
    cfg = {
        "strategy_id": strategy["id"],
        "params": {},
        "universe": codes,
        "start": str(start_date),
        "end": str(end_date),
        "init_cash": 100000,
        "cost": {"slippage": 0.0005, "fee": 0.0005}
    }

    bt = Backtester(cfg)
    result = bt.run()

    # 保存结果到数据库
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
        for k, v in result.metrics.items():
            s.add(Metrics(run_id=run_id, metric_name=k, metric_value=float(v)))
        for t, nav, dd in result.equity_curve.itertuples():
            s.add(EquityCurve(run_id=run_id, datetime=t, nav=nav, drawdown=dd))
        s.commit()

    # 前端展示结果
    st.success("✅ 回测完成！结果已写入数据库")
    st.write("### 回测指标")
    st.json(result.metrics)

    st.write("### 净值曲线")
    st.line_chart(result.equity_curve[["nav"]])

    st.write("### 回撤曲线")
    st.line_chart(result.equity_curve[["drawdown"]])
