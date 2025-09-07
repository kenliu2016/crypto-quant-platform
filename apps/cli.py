import os
import sys
# ===== 确保能导入 core/ =====
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # apps/
ROOT_DIR = os.path.dirname(CURRENT_DIR)                   # crypto-quant-platform/
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

import streamlit as st

# 定义页面映射
PAGES = {
    "🏠 首页 / 仪表盘": "apps/views/Dashboard.py",
    "📈 策略回测": "apps/views/Backtest.py",
    "🧪 测试运行": "apps/views/TestRun.py",
    "⚙️ 批量生成器": "apps/views/BatchGenerator.py",
    "🔔 通知中心": "apps/views/Notify.py",
    "📊 进度监控": "apps/views/Progress.py",
    "📑 报告中心": "apps/views/Reports.py",
    "🛠️ 参数调优": "apps/views/Tuning.py",
}

# 侧边栏导航
st.sidebar.title("📊 量化策略系统")
choice = st.sidebar.radio("导航", list(PAGES.keys()))

# 加载并执行页面代码
page_file = PAGES[choice]
if os.path.exists(page_file):
    with open(page_file, "r", encoding="utf-8") as f:
        code = f.read()
    exec(code, globals())
else:
    st.error(f"未找到页面文件: {page_file}")
