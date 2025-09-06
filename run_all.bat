@echo off
setlocal enabledelayedexpansion

REM === 1. 创建虚拟环境并安装依赖 ===
if not exist venv (
    echo >>> 创建 Python 虚拟环境
    python -m venv venv
)

echo >>> 激活虚拟环境
call venv\Scripts\activate

echo >>> 安装依赖
pip install -r requirements.txt

REM === 2. 初始化数据库 ===
echo >>> 初始化数据库 schema
psql -U postgres -h localhost -c "CREATE DATABASE quant;" || echo 数据库 quant 已存在

psql -U postgres -h localhost -d quant -f db\schema.sql
psql -U postgres -h localhost -d quant -f db\init_strategies.sql

REM === 3. 启动 Streamlit 仪表盘 ===
echo >>> 启动 Streamlit 仪表盘 (http://localhost:8501)
streamlit run apps\dashboard\Home.py