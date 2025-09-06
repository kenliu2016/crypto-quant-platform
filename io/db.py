from sqlalchemy import create_engine  # 引入依赖库
from sqlalchemy.orm import sessionmaker  # 引入依赖库
import os  # 引入依赖库

DB_URL = os.getenv("STREAMLIT_SECRET_db_url") or "postgresql+psycopg2://USER:PASS@HOST:5432/DB"  # 变量赋值
engine = create_engine(DB_URL, pool_pre_ping=True, future=True)  # 变量赋值
Session = sessionmaker(bind=engine)  # 变量赋值
