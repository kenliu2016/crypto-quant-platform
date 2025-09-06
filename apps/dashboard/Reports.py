import streamlit as st, pandas as pd, sqlalchemy as sa, json  # 引入依赖库
engine = sa.create_engine(st.secrets.get("db_url","postgresql+psycopg2://USER:PASS@HOST:5432/DB"))  # 变量赋值
st.title("📈 Reports")  # 函数调用
runs = pd.read_sql(sa.text("SELECT run_id FROM run ORDER BY started_at DESC LIMIT 100"), engine)  # 变量赋值
rid = st.selectbox("选择 run", runs["run_id"].tolist())  # 变量赋值
if rid:  # 条件判断
    eq = pd.read_sql(sa.text("SELECT datetime, nav FROM equity_curve WHERE run_id=:rid ORDER BY datetime"),  # 变量赋值
                     engine, params={"rid": rid}, parse_dates=["datetime"]).set_index("datetime")  # 变量赋值
    st.line_chart(eq["nav"])  # 函数调用
    ms = pd.read_sql(sa.text("SELECT metric_name, metric_value FROM metrics WHERE run_id=:rid"), engine, params={"rid": rid})  # 变量赋值
    st.dataframe(ms.pivot_table(values="metric_value", index="metric_name"))  # 变量赋值
    st.download_button("导出 Excel (指标+净值)", data=eq.to_csv(), file_name=f"{rid}.csv")  # 变量赋值
