"""
统一数据库连接封装模块
- 支持 psycopg2 与 SQLAlchemy
- 从 config/db_config.yaml 读取；支持环境变量覆盖：PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD
- 同时兼容配置文件里的 dbname/database 字段
"""
from __future__ import annotations
import os
from core.db import get_connection, get_engine
from typing import Dict, Any

import yaml

try:
    import psycopg2
except Exception:
    psycopg2 = None

try:
    from sqlalchemy import create_engine
except Exception:
    create_engine = None

DEFAULT_CONFIG_PATH = os.environ.get("DB_CONFIG", "config/db_config.yaml")

def load_db_config(config_path: str | None = None) -> Dict[str, Any]:
    """
    加载数据库配置；优先参数，其次环境变量 DB_CONFIG，最后默认路径。
    环境变量覆盖：PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD
    """
    path = config_path or DEFAULT_CONFIG_PATH
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    pg = dict(raw.get("postgres", {}))
    # 兼容 dbname/database 命名
    dbname = pg.get("dbname") or pg.get("database")
    pg["dbname"] = dbname
    # 环境变量覆盖
    if os.environ.get("PGHOST"):
        pg["host"] = os.environ["PGHOST"]
    if os.environ.get("PGPORT"):
        try:
            pg["port"] = int(os.environ["PGPORT"])
        except ValueError:
            pg["port"] = os.environ["PGPORT"]
    if os.environ.get("PGDATABASE"):
        pg["dbname"] = os.environ["PGDATABASE"]
    if os.environ.get("PGUSER"):
        pg["user"] = os.environ["PGUSER"]
    if os.environ.get("PGPASSWORD"):
        pg["password"] = os.environ["PGPASSWORD"]
    # 默认端口
    pg.setdefault("port", 5432)
    return pg

def get_connection(config_path: str | None = None):
    """返回 psycopg2 连接"""
    if psycopg2 is None:
        raise ImportError("未安装 psycopg2，请先 `pip install psycopg2-binary`")
    pg = load_db_config(config_path)
    conn = get_connection()
    return conn

def get_engine(config_path: str | None = None):
    """返回 SQLAlchemy Engine"""
    if create_engine is None:
        raise ImportError("未安装 SQLAlchemy，请先 `pip install sqlalchemy psycopg2-binary`")
    pg = load_db_config(config_path)
    url = f"postgresql+psycopg2://{pg['user']}:{pg['password']}@{pg['host']}:{pg['port']}/{pg['dbname']}"
    engine = get_engine()
    return engine
