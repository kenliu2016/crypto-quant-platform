
import streamlit as st  # 引入依赖库
import pandas as pd  # 引入依赖库
import altair as alt  # 引入依赖库
import numpy as np  # 引入依赖库

try:
    import plotly.graph_objects as go  # 引入依赖库
    PLOTLY_OK = True  # 变量赋值
except Exception:
    PLOTLY_OK = False  # 变量赋值

st.set_page_config(page_title="量化策略管理平台", layout="wide")  # 变量赋值

# ------------------------------
# 数据源（示例：可替换为数据库查询）
# ------------------------------
# 定义函数 load_strategy_comparison，实现具体功能逻辑
def load_strategy_comparison():
    data = [  # 变量赋值
        ["时间序列动量", "趋势跟随，高回撤", "趋势行情，BTC/ETH 等主流币", "夏普率、卡玛比"],
        ["横截面动量", "多空对冲，中性", "多品种组合，分散风险", "IC、RankIC、胜率"],
        ["均值回归（布林/配对）", "高频交易，均值回归", "震荡市场，协整资产对", "盈亏比、胜率"],
        ["因子多空", "多因子组合，中风险", "中长期投资，风格暴露", "夏普、因子 IC"],
        ["机器学习", "依赖训练数据", "特征充分，需回测验证", "AUC、F1、命中率"],
        ["网格交易", "稳健，低波动", "震荡行情，USDT 交易对", "总收益、回撤"],
        ["做市（被动挂单）", "稳定收手续费，高资金需求", "高流动性币对", "手续费收入、换手率"],
        ["动量+波动率双因子", "趋势+防御", "大类资产配置，择优筛选", "夏普、波动率、回撤"],
    ]
    return pd.DataFrame(data, columns=["策略类别", "风险特征", "适用市场/场景", "典型指标"])  # 变量赋值

# 定义函数 load_strategy_metrics，实现具体功能逻辑
def load_strategy_metrics():
    """模拟一些策略回测指标。生产环境请直接从 metrics 表汇总。"""
    data = {  # 变量赋值
        "策略类别": [
            "时间序列动量", "横截面动量", "均值回归（布林/配对）", "因子多空",
            "机器学习", "网格交易", "做市（被动挂单）", "动量+波动率双因子"
        ],
        "夏普率": [1.2, 1.0, 0.8, 1.1, 1.3, 0.9, 0.7, 1.4],
        "最大回撤": [-0.25, -0.18, -0.15, -0.22, -0.30, -0.10, -0.08, -0.20],
        "年化收益率": [0.28, 0.22, 0.18, 0.24, 0.32, 0.15, 0.12, 0.30],
        "胜率": [0.52, 0.55, 0.58, 0.54, 0.56, 0.60, 0.62, 0.57],
        "盈亏比": [1.35, 1.25, 1.10, 1.28, 1.40, 1.05, 0.95, 1.45]
    }
    return pd.DataFrame(data)  # 返回结果

# ------------------------------
# 组件：策略对比表
# ------------------------------
# 定义函数 show_strategy_comparison，实现具体功能逻辑
def show_strategy_comparison():
    st.subheader("📊 策略对比表")  # 函数调用
    df = load_strategy_comparison()  # 变量赋值
    st.dataframe(df, use_container_width=True)  # 变量赋值
    csv = df.to_csv(index=False).encode("utf-8")  # 变量赋值
    st.download_button(
        label="📥 下载对比表 (CSV)",  # 变量赋值
        data=csv,  # 变量赋值
        file_name="strategy_comparison.csv",  # 变量赋值
        mime="text/csv"  # 变量赋值
    )

# ------------------------------
# 组件：指标选择器 + 单指标柱状图
# ------------------------------
METRIC_OPTIONS = ["夏普率", "最大回撤", "年化收益率", "胜率", "盈亏比"]  # 变量赋值

# 定义函数 show_metric_selector_and_chart，实现具体功能逻辑
def show_metric_selector_and_chart():
    st.subheader("📈 指标对比")  # 函数调用
    metrics_df = load_strategy_metrics()  # 变量赋值

    col1, col2 = st.columns([2,1])  # 变量赋值
    with col1:
        metric = st.selectbox("选择要对比的指标", METRIC_OPTIONS, index=0)  # 变量赋值
    with col2:
        sort_desc = st.checkbox("按值降序排序", value=True)  # 变量赋值

    plot_df = metrics_df[["策略类别", metric]].copy()  # 变量赋值
    if sort_desc:  # 条件判断
        plot_df = plot_df.sort_values(by=metric, ascending=False)  # 变量赋值

    # 颜色不固定，使用 Altair 默认
    chart = alt.Chart(plot_df).mark_bar().encode(  # 变量赋值
        x=alt.X("策略类别:N", sort=None),  # 变量赋值
        y=alt.Y(f"{metric}:Q"),  # 变量赋值
        tooltip=["策略类别", metric]  # 变量赋值
    ).properties(title=f"各策略 {metric} 对比")  # 变量赋值
    st.altair_chart(chart, use_container_width=True)  # 变量赋值

# ------------------------------
# 组件：多指标雷达图
# ------------------------------
RADAR_METRICS_DEFAULT = ["夏普率", "年化收益率", "胜率", "盈亏比", "最大回撤"]  # 变量赋值

# 定义函数 normalize_for_radar，实现具体功能逻辑
def normalize_for_radar(df: pd.DataFrame, metrics: list[str]) -> pd.DataFrame:
    """将不同量纲的指标归一化到 [0, 1]，回撤取反向（越小越好→越大越好）。"""
    df = df.copy()  # 变量赋值
    for m in metrics:  # 循环遍历
        series = df[m].astype(float)  # 变量赋值
        # 对于回撤：负数越小越差 ⇒ 先取绝对值，再反向评分
        if "回撤" in m:  # 条件判断
            series = -series  # -(-0.25)=0.25，越大越差
            max_v, min_v = series.max(), series.min()  # 变量赋值
            norm = (series - min_v) / (max_v - min_v + 1e-9)  # 变量赋值
            score = 1 - norm  # 0=差,1=好
        else:
            max_v, min_v = series.max(), series.min()  # 变量赋值
            score = (series - min_v) / (max_v - min_v + 1e-9)  # 变量赋值
        df[m] = score  # 变量赋值
    return df  # 返回结果

# 定义函数 show_radar_chart，实现具体功能逻辑
def show_radar_chart():
    st.subheader("🕸️ 多指标雷达图")  # 函数调用
    df = load_strategy_metrics()  # 变量赋值
    metrics_to_use = st.multiselect("选择雷达图指标（可多选）", METRIC_OPTIONS, default=RADAR_METRICS_DEFAULT)  # 变量赋值
    if len(metrics_to_use) < 3:  # 条件判断
        st.info("请至少选择 3 个指标用于雷达图。")  # 函数调用
        return

    norm_df = normalize_for_radar(df, metrics_to_use)  # 变量赋值

    # radar 需要闭合多边形
    categories = metrics_to_use  # 变量赋值
    if PLOTLY_OK:  # 条件判断
        fig = go.Figure()  # 变量赋值
        for _, row in norm_df.iterrows():  # 循环遍历
            values = [row[m] for m in categories]  # 变量赋值
            values += values[:1]  # 变量赋值
            fig.add_trace(go.Scatterpolar(
                r=values,  # 变量赋值
                theta=categories + [categories[0]],  # 变量赋值
                fill='toself',  # 变量赋值
                name=row["策略类别"]  # 变量赋值
            ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0,1])),  # 变量赋值
            showlegend=True,  # 变量赋值
            title="策略综合评分（归一化后，越大越好）"  # 变量赋值
        )
        st.plotly_chart(fig, use_container_width=True)  # 变量赋值
    else:
        st.warning("未安装 plotly 库，无法显示雷达图。请在环境中安装：pip install plotly")  # 函数调用

# ------------------------------
# 页面装配
# ------------------------------
st.title("量化策略管理平台")  # 函数调用
st.write("欢迎使用统一策略管理与回测平台 🚀")  # 函数调用

show_strategy_comparison()  # 函数调用
show_metric_selector_and_chart()  # 函数调用
show_radar_chart()  # 函数调用
