import sys
import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

import streamlit as st, pandas as pd, sqlalchemy as sa, uuid, json
from datetime import datetime
from core.backtester import Backtester
from core.db import get_engine

engine = get_engine()

def run_backtest(cfg):
    bt = Backtester(cfg)
    result = bt.run()
    rid = str(uuid.uuid4())

    conn = engine.connect()
    try:
        conn.execute(sa.text("""
            INSERT INTO run (run_id, started_at, strategy_id, config, status)
            VALUES (:rid, :started_at, :strategy_id, :config, :status)
        """), {
            "rid": rid,
            "started_at": datetime.now(),
            "strategy_id": cfg.get("strategy_id", 0),
            "config": json.dumps(cfg),
            "status": "success"
        })

        for k, v in result.metrics.items():
            conn.execute(sa.text("""
                INSERT INTO metrics (run_id, metric_name, metric_value)
                VALUES (:rid, :metric_name, :metric_value)
            """), {"rid": rid, "metric_name": k, "metric_value": float(v)})

        for t, nav, dd in result.equity_curve.itertuples():
            conn.execute(sa.text("""
                INSERT INTO equity_curve (run_id, datetime, nav, drawdown)
                VALUES (:rid, :datetime, :nav, :drawdown)
            """), {"rid": rid, "datetime": t, "nav": nav, "drawdown": dd})

        conn.commit()
    finally:
        conn.close()

    return rid

st.title("🧪 📈 策略回测 / 自动落库 & 对比 & 复现")

# --- 从数据库加载策略 ---
df_strategies = pd.read_sql(sa.text("SELECT id, name, description FROM strategies ORDER BY id"), engine)
strategy_map = {row["id"]: f"{row['name']} - {row['description']}" for _, row in df_strategies.iterrows()}

with st.form("bt_cfg"):
    strategy_id = st.selectbox("策略", options=list(strategy_map.keys()), format_func=lambda x: strategy_map[x])
    codes = st.multiselect("标的池", ["BTCUSDT","ETHUSDT","BNBUSDT"], default=["BTCUSDT","ETHUSDT"])
    start = st.text_input("开始", "2023-01-01")
    end = st.text_input("结束", "2025-09-05")
    fee = st.number_input("费率", value=0.001, step=0.0001)
    slip = st.number_input("滑点", value=0.0005, step=0.0001)
    sub = st.form_submit_button("运行回测并写库")

if sub:
    cfg = {
        "strategy_id": strategy_id,
        "universe": codes,
        "start": start,
        "end": end,
        "cost": {"fee": fee, "slippage": slip}
    }
    with st.spinner("Running..."):
        rid = run_backtest(cfg)
    st.success(f"完成 RUN_ID: {rid}")
    st.session_state.setdefault("recent_runs", []).insert(0, rid)

# 最近运行
st.subheader("最近运行")
df_recent = pd.read_sql(sa.text("SELECT run_id, started_at, strategy_id FROM run ORDER BY started_at DESC LIMIT 20"), engine)
st.dataframe(df_recent)

# 多 run 对比
st.subheader("多 run 对比")
choices = df_recent["run_id"].tolist()
sel = st.multiselect("选择 run_id", choices, max_selections=8, default=choices[:3])
if sel:
    dfs = []
    for rid in sel:
        d = pd.read_sql(sa.text("SELECT datetime, nav FROM equity_curve WHERE run_id=:rid ORDER BY datetime"),
                        engine, params={"rid": rid}, parse_dates=["datetime"])
        d["run_id"] = rid
        dfs.append(d)
    if dfs:
        eq = pd.concat(dfs, ignore_index=True)
        st.line_chart(eq.pivot(index="datetime", columns="run_id", values="nav"))
