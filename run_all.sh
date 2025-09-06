#!/bin/bash
set -e

# === 1. 创建虚拟环境并安装依赖 ===
if [ ! -d "venv" ]; then
  echo ">>> 创建 Python 虚拟环境"
  python3 -m venv venv
fi

echo ">>> 激活虚拟环境"
source venv/bin/activate

echo ">>> 安装依赖"
pip install -r requirements.txt

# === 2. 初始化数据库 ===
echo ">>> 初始化数据库 schema"
psql -U cfs -h localhost -c "CREATE DATABASE quant;" || echo "数据库 quant 已存在"

psql -U cfs -h localhost -d quant -f db/schema.sql
psql -U cfs -h localhost -d quant -f db/init_strategies.sql

# === 3. 启动 Streamlit 仪表盘 ===
echo ">>> 启动 Streamlit 仪表盘 (http://localhost:8501)"
streamlit run apps/pages/Home.py