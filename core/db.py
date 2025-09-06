"""
统一数据库连接封装模块
- 支持 psycopg2 与 SQLAlchemy
- 从 config/db_config.yaml 读取；支持环境变量覆盖
- 环境变量覆盖：PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD
"""

import os
from typing import Dict, Any, Optional
import yaml

try:
    import psycopg2
except ImportError:
    psycopg2 = None

try:
    from sqlalchemy import create_engine
except ImportError:
    create_engine = None

DEFAULT_CONFIG_PATH = os.environ.get("DB_CONFIG", "config/db_config.yaml")


def load_db_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    加载数据库配置。
    优先级：参数 > 环境变量 DB_CONFIG > 默认路径。
    环境变量覆盖：PGHOST, PGPORT, PGDATABASE, PGUSER, PGPASSWORD
    """
    path = config_path or DEFAULT_CONFIG_PATH
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    pg = dict(raw.get("postgres", {}))
    # 兼容 dbname / database 两种命名
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


def get_connection(config_path: Optional[str] = None):
    """返回 psycopg2 连接"""
    if psycopg2 is None:
        raise ImportError("未安装 psycopg2，请先执行: pip install psycopg2-binary")

    pg = load_db_config(config_path)
    conn = psycopg2.connect(
        host=pg["host"],
        port=pg["port"],
        dbname=pg["dbname"],
        user=pg["user"],
        password=pg["password"],
    )
    return conn


def get_engine(config_path: Optional[str] = None):
    """返回 SQLAlchemy Engine"""
    if create_engine is None:
        raise ImportError("未安装 SQLAlchemy，请先执行: pip install sqlalchemy psycopg2-binary")

    import urllib.parse
    
    pg = load_db_config(config_path)
    # 对用户名和密码进行URL编码，处理特殊字符如@
    user = urllib.parse.quote_plus(pg['user'])
    password = urllib.parse.quote_plus(pg['password'])
    
    url = f"postgresql+psycopg2://{user}:{password}@{pg['host']}:{pg['port']}/{pg['dbname']}"

    # ✅ 这里用 sqlalchemy.create_engine，而不是递归调用自己
    engine = create_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=10)
    return engine
