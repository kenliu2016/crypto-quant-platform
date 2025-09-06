# tests/test_pages_db.py
"""
回归测试脚本：验证 apps/pages 下的页面是否能正常使用数据库封装
不会启动 Streamlit，只检查数据库连接是否可用
"""

import importlib
import pkgutil
import os
from core.db import get_connection, get_engine

def test_db_connection():
    """基础数据库连通性测试"""
    print("=== 基础数据库连通性测试 ===")
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT 1;")
        print("psycopg2 查询结果:", cur.fetchone())
    conn.close()

    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute("SELECT 2;")
        print("SQLAlchemy 查询结果:", result.fetchone())
    print("✅ 数据库封装连接测试通过\n")

def test_pages_import():
    """尝试导入 apps/pages 下的所有模块"""
    print("=== 导入 apps/pages 下所有模块 ===")
    pages_dir = os.path.join(os.path.dirname(__file__), "..", "apps", "pages")
    package_name = "apps.pages"

    for _, module_name, _ in pkgutil.iter_modules([pages_dir]):
        full_module_name = f"{package_name}.{module_name}"
        try:
            importlib.import_module(full_module_name)
            print(f"✅ 成功导入模块: {full_module_name}")
        except Exception as e:
            print(f"❌ 导入模块失败: {full_module_name} | 错误: {e}")

if __name__ == "__main__":
    test_db_connection()
    test_pages_import()
    print("\n=== 回归测试完成 ===")
