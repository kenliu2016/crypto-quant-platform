import streamlit as st, pandas as pd, itertools  # 引入依赖库
from apps.cli import run_backtest  # 引入依赖库

st.title("🧩 通用批量回测任务生成器")  # 函数调用
strategy = st.text_input("策略名", "TSMA")  # 变量赋值
codes = [c.strip() for c in st.text_area("标的池(逗号分隔)", "BTCUSDT,ETHUSDT").split(",") if c.strip()]  # 变量赋值
start = st.date_input("开始日期")  # 变量赋值
end = st.date_input("结束日期")  # 变量赋值
fee_rate = st.number_input("费率", value=0.001, step=0.0001)  # 变量赋值

st.subheader("固定参数")  # 函数调用
fixed_params = {}  # 变量赋值
nf = st.number_input("固定参数数量", 0, 10, 1)  # 变量赋值
for i in range(nf):  # 循环遍历
    k = st.text_input(f"固定参数名 {i+1}", key=f"fk{i}")  # 变量赋值
    v = st.text_input(f"固定参数值 {i+1}", key=f"fv{i}")  # 变量赋值
    if k:  # 条件判断
        try: v = eval(v)  # 变量赋值
        except: pass
        fixed_params[k]=v  # 变量赋值

st.subheader("网格参数")  # 函数调用
grid_params = {}  # 变量赋值
ng = st.number_input("网格参数数量", 0, 10, 2)  # 变量赋值
for i in range(ng):  # 循环遍历
    k = st.text_input(f"网格参数名 {i+1}", key=f"gk{i}")  # 变量赋值
    vals = st.text_input(f"候选值(逗号)", key=f"gv{i}")  # 变量赋值
    if k and vals:  # 条件判断
        try:
            arr = [eval(x) for x in vals.split(",")]  # 变量赋值
        except:
            arr = vals.split(",")  # 变量赋值
        grid_params[k]=arr  # 变量赋值

if st.button("生成并提交"):  # 条件判断
    if grid_params:  # 条件判断
        keys, values = zip(*grid_params.items())  # 变量赋值
        combos = [dict(zip(keys, v)) for v in itertools.product(*values)]  # 变量赋值
    else:
        combos = [{}]  # 变量赋值
    tasks = []  # 变量赋值
    for code in codes:  # 循环遍历
        for combo in combos:  # 循环遍历
            row = {"strategy": strategy, "codes": code, "start": str(start), "end": str(end), "fee_rate": fee_rate}  # 变量赋值
            row.update(fixed_params); row.update(combo)  # 函数调用
            tasks.append(row)  # 函数调用
    df = pd.DataFrame(tasks)  # 变量赋值
    st.dataframe(df)  # 函数调用
    for cfg in tasks:  # 循环遍历
        run_backtest(cfg)  # 可替换为异步队列
    st.success(f"已提交 {len(tasks)} 个任务")  # 函数调用
    st.download_button("下载任务 CSV", data=df.to_csv(index=False), file_name=f"batch_{strategy}.csv")  # 变量赋值
