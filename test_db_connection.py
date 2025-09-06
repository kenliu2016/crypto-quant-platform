#!/usr/bin/env python
# 数据库连接测试脚本
import os
import sys
import urllib.parse

# 添加项目根目录到路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)

# 打印环境变量信息
env_vars = ['PGHOST', 'PGPORT', 'PGDATABASE', 'PGUSER', 'PGPASSWORD']
print("环境变量检查:")
for var in env_vars:
    print(f"{var} = {os.environ.get(var, '未设置')}")

# 检查core/db.py中的连接字符串生成
from core.db import load_db_config, get_engine

print("\n配置加载检查:")
pg_config = load_db_config()
print(f"加载的配置: {pg_config}")

# 手动构建正确的URL编码连接字符串
user = urllib.parse.quote_plus(pg_config['user'])
password = urllib.parse.quote_plus(pg_config['password'])
encoded_url = f"postgresql+psycopg2://{user}:{password}@{pg_config['host']}:{pg_config['port']}/{pg_config['dbname']}"
print(f"URL编码后的连接字符串: {encoded_url}")

# 测试修复后的get_engine函数
try:
    print("\n测试修复后的get_engine函数...")
    engine = get_engine()
    # 尝试连接
    with engine.connect() as conn:
        print("✅ get_engine连接成功!")
except Exception as e:
    print(f"❌ get_engine连接失败: {str(e)}")

# 尝试直接使用URL编码的连接字符串
try:
    from sqlalchemy import create_engine
    print("\n尝试使用URL编码的连接字符串...")
    encoded_engine = create_engine(encoded_url)
    # 尝试连接
    with encoded_engine.connect() as conn:
        print("✅ URL编码连接字符串成功!")
except Exception as e:
    print(f"❌ URL编码连接字符串失败: {str(e)}")

# 尝试原始psycopg2连接
try:
    import psycopg2
    print("\n尝试psycopg2连接...")
    conn = psycopg2.connect(
        host=pg_config['host'],
        port=pg_config['port'],
        dbname=pg_config['dbname'],
        user=pg_config['user'],
        password=pg_config['password']
    )
    print("✅ psycopg2连接成功!")
    conn.close()
except Exception as e:
    print(f"❌ psycopg2连接失败: {str(e)}")

print("\n测试完成！")