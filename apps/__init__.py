# apps包初始化文件

# 确保io模块可以被正确导入
import sys
import os

# 将项目根目录添加到sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)