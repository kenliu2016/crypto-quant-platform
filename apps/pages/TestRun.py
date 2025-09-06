"""
Streamlit 页面: 一键运行测试回测
功能:
1. 从数据库加载已注册的策略
2. 用户选择标的、时间区间和策略
3. 运行快速回测（假数据或历史K线）
4. 展示净值曲线、回撤、夏普率等指标
"""
import sys
import os
# ========= 自动加入项目根目录到 sys.path =========
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))      # apps/pages/
ROOT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))      # crypto-quant-platform/
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)
import streamlit as st
import pandas as pd
import numpy as np
import datetime
import uuid
from sqlalchemy import text

# ========= 导入项目模块 =========
from core.backtester import Backtester
from core.db import get_engine
from data_io.schemas import Run, Metrics, EquityCurve
from sqlalchemy.orm import sessionmaker

# 创建session
engine = get_engine()
Session = sessionmaker(bind=engine)


# ============ 工具函数 ============

def load_strategies():
    """加载数据库里所有已注册的策略"""
    with Session() as s:
        rows = s.execute(text("SELECT id, name, description FROM strategies ORDER BY id")).fetchall()
        return [dict(r._mapping) for r in rows]


def generate_dummy_data(codes, start, end):
    """生成测试数据 (分钟K线)"""
    idx = pd.date_range(start=start, end=end, freq="1min")
    data = []
    for code in codes:
        price = 100 + np.cumsum(np.random.randn(len(idx)))  # 随机游走
        df = pd.DataFrame({
            "datetime": idx,
            "code": code,
            "open": price,
            "hight": price * (1 + 0.001),
            "low": price * (1 - 0.001),
            "close": price,
            "volume": np.random.randint(100, 1000, size=len(idx))
        })
        data.append(df)
    return pd.concat(data).set_index(["datetime", "code"]).sort_index()


# ============ 页面布局 ============

st.title("🚀 快速回测测试 (TestRun)")

# 策略选择
strategies = load_strategies()
strategy_options = {s["name"]: s for s in strategies}
strategy_name = st.selectbox("选择策略", list(strategy_options.keys()))

# 标的选择
codes = st.multiselect("选择交易标的", ["BTCUSDT", "ETHUSDT", "BNBUSDT"], default=["BTCUSDT"])

# 时间区间
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("开始日期", datetime.date(2024, 1, 1))
with col2:
    end_date = st.date_input("结束日期", datetime.date(2024, 1, 15))

# 执行按钮
if st.button("运行回测 🚦"):
    run_id = str(uuid.uuid4())
    st.write(f"运行ID: `{run_id}`")

    # 加载策略
    strategy = strategy_options[strategy_name]
    st.write(f"使用策略: **{strategy['name']}**")
    st.write(strategy["description"])

    # 生成测试数据
    data = generate_dummy_data(codes, start_date, end_date)

    # 构造配置
    cfg = {
        "strategy_id": strategy["id"],
        "params": {},  # 默认空参数，可以以后扩展成表单输入
        "codes": codes,
        "start": str(start_date),
        "end": str(end_date),
        "initial_capital": 100000,
        "slippage": 0.0005,
        "fee": 0.0005,
    }

    # 执行回测
    bt = Backtester(cfg, data)
    result = bt.run()

    # 保存数据库
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
