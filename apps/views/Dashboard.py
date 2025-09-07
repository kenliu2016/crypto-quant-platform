import streamlit as st

st.title("🏠 首页 / 仪表盘")

# 卡片式入口
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("📈 策略回测")
    st.write("基于历史数据对交易策略进行回测")
    if st.button("进入回测", key="to_backtest"):
        st.switch_page("pages/Backtest.py")

with col2:
    st.subheader("🔮 行情预测")
    st.write("基于模型预测未来价格走势")
    if st.button("进入报告", key="to_reports"):
        st.switch_page("pages/Reports.py")

with col3:
    st.subheader("⚠️ 风险分析")
    st.write("评估交易风险，优化仓位管理")
    if st.button("进入风险分析", key="to_risk"):
        st.switch_page("pages/Tuning.py")

st.divider()

# 示例：保留原 run_dashboard 的监控逻辑
st.subheader("📊 市场监控")
st.line_chart([1, 5, 2, 6, 9, 4])
