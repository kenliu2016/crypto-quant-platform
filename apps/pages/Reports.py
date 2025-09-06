# apps/pages/Reports.py
# -*- coding: utf-8 -*-
"""
回测报告中心（Reports）
- 批量对比多个 run 的净值曲线（overlay）
- 单个 run 详情：指标、净值/回撤、交易明细（带筛选与统计）
- 导出 PDF / Excel 报告
- 可选自动刷新
"""
import base64
from io import BytesIO

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table
from sqlalchemy import create_engine, text
from core.db import get_connection, get_engine
# =========================
# 🔧 数据库连接（请修改）
# =========================
DB_URL = "postgresql://postgres:yourpassword@localhost:5432/quant"
engine = get_engine()

# =========================
# ⚙️ 页面设置
# =========================
st.set_page_config(page_title="回测报告中心", layout="wide")
st.title("📊 回测报告中心")

# 侧边栏：自动刷新
with st.sidebar:
    st.header("⚙️ 运行设置")
    enable_autorefresh = st.checkbox("实时自动刷新（5s）", value=False)
    if enable_autorefresh:
        st.experimental_rerun  # 仅为类型提示
        st_autorefresh_count = st.experimental_rerun if False else None
        st_autorefresh_count = st.autorefresh(interval=5000, key="reports_autorefresh")

# =========================
# 载入 run 列表
# =========================
with engine.begin() as conn:
    runs = pd.read_sql(
        text("SELECT run_id, strategy_id, run_type, started_at, ended_at, status FROM run ORDER BY started_at DESC"),
        conn,
    )

if runs.empty:
    st.info("暂无回测记录，请先运行一次回测。")
    st.stop()

# =========================
# 📈 批量 run overlay 对比
# =========================
st.subheader("📈 批量净值曲线对比（Overlay）")

col_sel, col_opt = st.columns([2, 1])
with col_sel:
    selected_runs = st.multiselect(
        "选择多个 run_id 进行对比",
        runs["run_id"].tolist(),
        default=runs["run_id"].head(2).tolist(),
    )
with col_opt:
    show_drawdown_overlay = st.checkbox("同时显示回撤曲线（次坐标）", value=False)

if selected_runs:
    fig_multi = go.Figure()
    dd_added = False
    with engine.begin() as conn:
        for rid in selected_runs:
            eq = pd.read_sql(
                text("SELECT datetime, nav, drawdown FROM equity_curve WHERE run_id=:rid ORDER BY datetime ASC"),
                conn,
                params={"rid": rid},
            )
            if eq.empty:
                continue
            # 净值曲线
            fig_multi.add_trace(
                go.Scatter(
                    x=eq["datetime"],
                    y=eq["nav"],
                    mode="lines",
                    name=f"{rid[:8]}…(NAV)",
                )
            )
            # 可选回撤曲线（使用次坐标，仅添加一次 y2 轴定义）
            if show_drawdown_overlay:
                fig_multi.add_trace(
                    go.Scatter(
                        x=eq["datetime"],
                        y=eq["drawdown"],
                        mode="lines",
                        name=f"{rid[:8]}…(DD)",
                        yaxis="y2",
                        line=dict(dash="dot"),
                    )
                )
                dd_added = True

    layout = dict(
        height=520,
        legend=dict(orientation="h", y=-0.25),
        xaxis=dict(title="时间"),
        yaxis=dict(title="净值"),
        margin=dict(l=40, r=40, t=40, b=40),
        title="批量净值曲线对比",
    )
    if dd_added:
        layout["yaxis2"] = dict(title="回撤", overlaying="y", side="right", showgrid=False)
    fig_multi.update_layout(**layout)
    st.plotly_chart(fig_multi, use_container_width=True)
else:
    st.info("请至少选择一个 run 进行对比。")

st.markdown("---")

# =========================
# 🔍 单个 run 详情
# =========================
st.subheader("🔍 单个回测详情")

run_id = st.selectbox("选择查看的 run_id", runs["run_id"].tolist())
with engine.begin() as conn:
    metrics = pd.read_sql(text("SELECT metric_name, metric_value FROM metrics WHERE run_id=:rid"), conn, params={"rid": run_id})
    equity = pd.read_sql(
        text("SELECT datetime, nav, drawdown FROM equity_curve WHERE run_id=:rid ORDER BY datetime ASC"),
        conn,
        params={"rid": run_id},
    )
    # 交易表优先读取 trades（含 pnl）；若不存在可改为 orders
    try:
        trades = pd.read_sql(
            text("SELECT datetime, code, side, qty, price, pnl FROM trades WHERE run_id=:rid ORDER BY datetime ASC"),
            conn,
            params={"rid": run_id},
        )
    except Exception:
        trades = pd.read_sql(
            text("SELECT datetime, code, side, qty, price FROM orders WHERE run_id=:rid ORDER BY datetime ASC"),
            conn,
            params={"rid": run_id},
        )
        trades["pnl"] = 0.0  # 没有 pnl 列时填充 0，避免后续统计报错

# —— 指标表
st.markdown("### 📑 指标")
if metrics.empty:
    st.info("该回测暂无指标数据。")
else:
    st.dataframe(metrics, use_container_width=True)

# —— 净值与回撤
st.markdown("### 📉 净值曲线与回撤")
if equity.empty:
    st.info("该回测暂无净值数据。")
else:
    fig_single = go.Figure()
    fig_single.add_trace(go.Scatter(x=equity["datetime"], y=equity["nav"], name="净值(NAV)"))
    fig_single.add_trace(go.Scatter(x=equity["datetime"], y=equity["drawdown"], name="回撤(DD)", yaxis="y2"))
    fig_single.update_layout(
        height=520,
        legend=dict(orientation="h", y=-0.25),
        xaxis=dict(title="时间"),
        yaxis=dict(title="净值"),
        yaxis2=dict(title="回撤", overlaying="y", side="right", showgrid=False),
        margin=dict(l=40, r=40, t=40, b=40),
        title=f"Run {run_id[:8]}… 净值/回撤",
    )
    st.plotly_chart(fig_single, use_container_width=True)

# =========================
# 🧾 交易明细 + 筛选 + 统计
# =========================
st.markdown("### 📝 交易明细（带筛选）")
if trades.empty:
    st.info("该回测暂无交易记录。")
else:
    # —— 构建筛选器
    col_a, col_b, col_c = st.columns([1, 1, 2])
    with col_a:
        side_options = ["全部"] + sorted(trades["side"].dropna().unique().tolist())
        selected_side = st.selectbox("方向", side_options, index=0)
    with col_b:
        # 盈亏范围（基于 pnl）
        min_pnl, max_pnl = float(trades["pnl"].min()), float(trades["pnl"].max())
        pnl_range = st.slider("盈亏范围（含）", min_pnl, max_pnl, (min_pnl, max_pnl))
    with col_c:
        codes = ["全部"] + sorted(trades["code"].dropna().unique().tolist())
        selected_code = st.selectbox("标的", codes, index=0)

    # —— 应用筛选
    filtered = trades.copy()
    if selected_side != "全部":
        filtered = filtered[filtered["side"] == selected_side]
    if selected_code != "全部":
        filtered = filtered[filtered["code"] == selected_code]
    filtered = filtered[(filtered["pnl"] >= pnl_range[0]) & (filtered["pnl"] <= pnl_range[1])]

    st.caption(f"共筛选到 {len(filtered)} 条交易记录")
    st.dataframe(filtered, use_container_width=True, height=320)

    # —— 统计
    if not filtered.empty:
        total_trades = len(filtered)
        win_trades = (filtered["pnl"] > 0).sum()
        win_rate = win_trades / total_trades if total_trades > 0 else 0.0
        avg_pnl = filtered["pnl"].mean()
        max_win = filtered["pnl"].max()
        max_loss = filtered["pnl"].min()

        stats_df = pd.DataFrame(
            {
                "胜率": [f"{win_rate:.2%}"],
                "平均盈亏": [f"{avg_pnl:.4f}"],
                "最大盈利": [f"{max_win:.4f}"],
                "最大亏损": [f"{max_loss:.4f}"],
                "交易次数": [total_trades],
            }
        )
        st.markdown("#### 📊 筛选结果统计")
        st.table(stats_df)

        # —— 盈亏柱状图（按时间顺序）
        st.markdown("#### 📉 盈亏柱状图（按交易顺序）")
        tmp = filtered.reset_index(drop=True).copy()
        tmp["idx"] = tmp.index + 1
        fig_bar = px.bar(tmp, x="idx", y="pnl", color="side", labels={"idx": "交易序号", "pnl": "盈亏"})
        st.plotly_chart(fig_bar, use_container_width=True)

# =========================
# 📤 导出报告（PDF / Excel）
# =========================
st.markdown("---")
st.subheader("📤 导出回测报告")

col_pdf, col_xls = st.columns(2)

# —— 导出 PDF
with col_pdf:
    if st.button("导出 PDF 报告"):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # 标题
        story.append(Paragraph(f"回测报告 - Run {run_id}", styles["Title"]))
        story.append(Spacer(1, 12))

        # 指标表
        if not metrics.empty:
            story.append(Paragraph("指标表", styles["Heading2"]))
            story.append(Table([metrics.columns.tolist()] + metrics.values.tolist()))
            story.append(Spacer(1, 12))

        # 净值曲线（Matplotlib 截图嵌入）
        if not equity.empty:
            fig, ax = plt.subplots()
            ax.plot(equity["datetime"], equity["nav"], label="净值")
            ax2 = ax.twinx()
            ax2.plot(equity["datetime"], equity["drawdown"], label="回撤", linestyle="--")
            ax.set_title("净值与回撤")
            ax.legend(loc="upper left")
            ax2.legend(loc="upper right")
            img_buf = BytesIO()
            plt.tight_layout()
            plt.savefig(img_buf, format="png", dpi=144)
            plt.close(fig)
            img_buf.seek(0)

            story.append(Paragraph("净值曲线与回撤", styles["Heading2"]))
            story.append(Image(img_buf, width=500, height=260))
            story.append(Spacer(1, 12))

        # 交易明细（前 20 行）
        if not trades.empty:
            preview = trades.head(20)
            story.append(Paragraph("交易明细（前 20 行）", styles["Heading2"]))
            story.append(Table([preview.columns.tolist()] + preview.values.tolist()))
            story.append(Spacer(1, 12))

        # 筛选结果统计（与页面一致，基于当前 filtered）
        try:
            if not trades.empty and "filtered" in locals() and not filtered.empty:
                total_trades = len(filtered)
                win_trades = (filtered["pnl"] > 0).sum()
                win_rate = win_trades / total_trades if total_trades > 0 else 0.0
                avg_pnl = filtered["pnl"].mean()
                max_win = filtered["pnl"].max()
                max_loss = filtered["pnl"].min()

                stats_data = [
                    ["交易次数", total_trades],
                    ["胜率", f"{win_rate:.2%}"],
                    ["平均盈亏", f"{avg_pnl:.6f}"],
                    ["最大盈利", f"{max_win:.6f}"],
                    ["最大亏损", f"{max_loss:.6f}"],
                ]
                story.append(Paragraph("筛选结果统计", styles["Heading2"]))
                story.append(Table(stats_data))
                story.append(Spacer(1, 12))
        except Exception:
            pass

        # 生成 PDF
        doc.build(story)
        buffer.seek(0)
        b64 = base64.b64encode(buffer.read()).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="report_{run_id}.pdf">📥 点击下载 PDF</a>'
        st.markdown(href, unsafe_allow_html=True)

# —— 导出 Excel
with col_xls:
    if st.button("导出 Excel 报告"):
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            if not metrics.empty:
                metrics.to_excel(writer, sheet_name="指标", index=False)
            if not equity.empty:
                equity.to_excel(writer, sheet_name="净值曲线", index=False)
            if not trades.empty:
                trades.to_excel(writer, sheet_name="交易明细_全量", index=False)
            if "filtered" in locals() and not filtered.empty:
                filtered.to_excel(writer, sheet_name="交易明细_筛选结果", index=False)
        buffer.seek(0)
        b64 = base64.b64encode(buffer.read()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="report_{run_id}.xlsx">📥 点击下载 Excel</a>'
        st.markdown(href, unsafe_allow_html=True)

# ============ 结束 ============
