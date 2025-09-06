import sys
import os
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# ========= 自动加入项目根目录到 sys.path =========
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# ========= 页面配置 =========
st.set_page_config(page_title="量化交易平台", layout="wide")
st.title("📊 量化交易策略管理平台 - 首页")
st.markdown("请选择需要进入的功能模块：")

# ========= 数据库配置 =========
DB_URL = "postgresql://user:password@localhost:5432/quantdb"  # ⚠️ 修改为实际配置
engine = create_engine(DB_URL)

# ========= 定义卡片 HTML 模板 =========
card_template = """
<div class="card">
  <h3>{title}</h3>
  <p>{desc}</p>
  <a href="?page={page}" target="_self" class="btn">{button}</a>
</div>
"""

# ========= 注入 CSS =========
st.markdown(
    """
    <style>
    .card {
        flex: 1 1 calc(45% - 20px);
        background-color: #f9f9f9;
        border-radius: 15px;
        padding: 20px;
        margin: 10px;
        border: 1px solid #ddd;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        min-width: 250px;
    }
    .card h3 { margin-top: 0; margin-bottom: 10px; }
    .card p { margin-bottom: 15px; color: #555; }
    .btn {
        display: inline-block;
        padding: 10px 20px;
        border-radius: 8px;
        background-color: #4CAF50;
        color: white;
        text-decoration: none;
        font-weight: bold;
    }
    .btn:hover { background-color: #45a049; }
    .card-container { display: flex; flex-wrap: wrap; justify-content: flex-start; }
    </style>
    """,
    unsafe_allow_html=True
)

# ========= 卡片容器 =========
st.markdown('<div class="card-container">', unsafe_allow_html=True)

cards = [
    {"title": "📈 策略回测", "desc": "运行历史行情回测，生成净值曲线和指标。",
     "page": "Backtest", "button": "进入回测页面 ➡️"},
    {"title": "⚙️ 策略调参", "desc": "使用 Optuna 等方法对策略参数进行自动化调优。",
     "page": "Tuning", "button": "进入调参页面 ➡️"},
    {"title": "📑 报告中心", "desc": "查看回测报告，下载 PDF/Excel 结果。",
     "page": "Reports", "button": "进入报告页面 ➡️"},
    {"title": "🧪 测试运行", "desc": "快速运行一个策略，验证逻辑是否正确。",
     "page": "TestRun", "button": "进入测试运行页面 ➡️"},
]

for card in cards:
    st.markdown(
        card_template.format(
            title=card["title"],
            desc=card["desc"],
            page=card["page"],
            button=card["button"],
        ),
        unsafe_allow_html=True
    )

st.markdown('</div>', unsafe_allow_html=True)

# ========= 最近运行结果预览 =========
st.markdown("---")
st.subheader("🕒 最近运行结果预览")

try:
    with engine.connect() as conn:
        query = text("""
        SELECT r.run_id, r.started_at, r.run_type, s.name AS strategy_name,
               MAX(CASE WHEN m.metric_name = 'sharpe' THEN m.metric_value END) AS sharpe,
               MAX(CASE WHEN m.metric_name = 'max_drawdown' THEN m.metric_value END) AS max_drawdown
        FROM run r
        LEFT JOIN strategy_registry s ON r.strategy_id = s.strategy_id
        LEFT JOIN metrics m ON r.run_id = m.run_id
        GROUP BY r.run_id, r.started_at, r.run_type, s.name
        ORDER BY r.started_at DESC
        LIMIT 5;
        """)
        df = pd.read_sql(query, conn)

    if df.empty:
        st.info("暂无运行记录，请先执行一次回测或调参。")
    else:
        # 给每条记录加“查看报告”按钮
        for i, row in df.iterrows():
            st.markdown(
                f"""
                <div style="padding:10px; margin-bottom:10px; border:1px solid #ddd; border-radius:10px;">
                    <b>Run ID:</b> {row['run_id']}  
                    <b>策略:</b> {row['strategy_name']} | <b>类型:</b> {row['run_type']}  
                    <b>开始时间:</b> {row['started_at']}  
                    <b>Sharpe:</b> {row['sharpe']:.2f} | <b>Max Drawdown:</b> {row['max_drawdown']:.2%}  
                    <a href="?page=Reports&run_id={row['run_id']}" target="_self"
                       style="display:inline-block; margin-top:8px; padding:6px 12px;
                              background-color:#2196F3; color:white; border-radius:6px;
                              text-decoration:none; font-weight:bold;">
                       📑 查看报告
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )

except Exception as e:
    st.error(f"数据库连接失败，请检查配置: {e}")
