import sys
import os

# ========= 自动加入项目根目录到 sys.path =========
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))      # apps/pages/
ROOT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))      # crypto-quant-platform/
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

import streamlit as st, pandas as pd, sqlalchemy as sa, json  # 引入依赖库
from streamlit_autorefresh import st_autorefresh  # 引入依赖库
engine = sa.create_engine(st.secrets.get("db_url","postgresql+psycopg2://USER:PASS@HOST:5432/DB"))  # 变量赋值
st.title("⏱ 回测任务进度")  # 函数调用
st_autorefresh(interval=30*1000, key="refresh")  # 变量赋值

df = pd.read_sql(sa.text("SELECT run_id, run_type, status, started_at, ended_at, config FROM run ORDER BY started_at DESC LIMIT 200"), engine)  # 变量赋值
st.dataframe(df)  # 函数调用

# 夏普榜单
metrics = pd.read_sql(sa.text("SELECT run_id, metric_name, metric_value FROM metrics WHERE metric_name='sharpe' AND run_id = ANY(:rids)"),  # 变量赋值
                      engine, params={"rids": df["run_id"].tolist()})  # 变量赋值
if not metrics.empty:  # 条件判断
    st.subheader("夏普率排行榜")  # 函数调用
    top = metrics.sort_values("metric_value", ascending=False).head(10)  # 变量赋值
    st.table(top)  # 函数调用

# 多任务 overlay
sel = st.multiselect("选择 run 叠加净值", df["run_id"].tolist(), default=df["run_id"].tolist()[:3], max_selections=8)  # 变量赋值
if sel:  # 条件判断
    dfs = []  # 变量赋值
    for rid in sel:  # 循环遍历
        d = pd.read_sql(sa.text("SELECT datetime, nav FROM equity_curve WHERE run_id=:rid ORDER BY datetime"),  # 变量赋值
                        engine, params={"rid": rid}, parse_dates=["datetime"]).set_index("datetime")  # 变量赋值
        d.rename(columns={"nav": rid}, inplace=True)  # 变量赋值
        dfs.append(d)  # 函数调用
    if dfs:  # 条件判断
        import pandas as pd  # 引入依赖库
        eq = pd.concat(dfs, axis=1)  # 变量赋值
        st.line_chart(eq)  # 函数调用
