import sys
import os
# ========= 自动加入项目根目录到 sys.path =========
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))      # apps/pages/
ROOT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))      # crypto-quant-platform/
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

import streamlit as st  # 引入依赖库
st.title("🧭 Tuning (placeholder)")  # 函数调用
st.info("接 Optuna/Walk-Forward，参考 tuning/ 目录。")  # 函数调用
