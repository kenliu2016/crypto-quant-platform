import sys
import os
# ========= 自动加入项目根目录到 sys.path =========
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))      # apps/pages/
ROOT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))      # crypto-quant-platform/
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

import streamlit as st, pandas as pd, sqlalchemy as sa, uuid, json  # 引入依赖库
from datetime import datetime  # 引入依赖库
from apps.cli import run_backtest  # 引入依赖库
from core.db import get_connection, get_engine

engine = get_engine() # 变量赋值

st.title("🧪 Backtest / 自动落库 & 对比 & 复现")  # 函数调用

with st.form("bt_cfg"):
    strategy_id = st.selectbox("策略", options=[1,2,3], format_func=lambda x:{1:"TSMA",2:"MeanRev",3:"PineAdapter"}[x])  # 变量赋值
    codes = st.multiselect("标的池", ["BTCUSDT","ETHUSDT","BNBUSDT"], default=["BTCUSDT","ETHUSDT"])  # 变量赋值
    start = st.text_input("开始", "2023-01-01")  # 变量赋值
    end = st.text_input("结束", "2025-09-05")  # 变量赋值
    fee = st.number_input("费率", value=0.001, step=0.0001)  # 变量赋值
    slip = st.number_input("滑点", value=0.0005, step=0.0001)  # 变量赋值
    sub = st.form_submit_button("运行回测并写库")  # 变量赋值

if sub:  # 条件判断
    cfg = {"strategy_id": strategy_id, "universe": codes, "start": start, "end": end, "cost":{"fee":fee,"slippage":slip}}  # 变量赋值
    with st.spinner("Running..."):
        rid = run_backtest(cfg)  # 变量赋值
    st.success(f"完成 RUN_ID: {rid}")  # 函数调用
    st.session_state.setdefault("recent_runs", []).insert(0, rid)  # 函数调用

st.subheader("最近运行")  # 函数调用
df_recent = pd.read_sql(sa.text("SELECT run_id, started_at, strategy_id FROM run ORDER BY started_at DESC LIMIT 20"), engine)  # 变量赋值
st.dataframe(df_recent)  # 函数调用

# 多 run 对比
st.subheader("多 run 对比")  # 函数调用
choices = df_recent["run_id"].tolist()  # 变量赋值
sel = st.multiselect("选择 run_id", choices, max_selections=8, default=choices[:3])  # 变量赋值
if sel:  # 条件判断
    dfs = []  # 变量赋值
    for rid in sel:  # 循环遍历
        d = pd.read_sql(sa.text("SELECT datetime, nav FROM equity_curve WHERE run_id=:rid ORDER BY datetime"),  # 变量赋值
                        engine, params={"rid": rid}, parse_dates=["datetime"])  # 变量赋值
        d["run_id"] = rid  # 变量赋值
        dfs.append(d)  # 函数调用
    if dfs:  # 条件判断
        eq = pd.concat(dfs, ignore_index=True)  # 变量赋值
        st.line_chart(eq.pivot(index="datetime", columns="run_id", values="nav"))  # 变量赋值
