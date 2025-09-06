from datetime import timedelta  # 引入依赖库
# 定义函数 generate_windows，实现具体功能逻辑
def generate_windows(start, end, train_days=30, test_days=7, step_days=7):  # 变量赋值
    cur = start  # 变量赋值
    while cur + timedelta(days=train_days+test_days) <= end:  # 变量赋值
        yield (cur, cur+timedelta(days=train_days)), (cur+timedelta(days=train_days), cur+timedelta(days=train_days+test_days))  # 变量赋值
        cur += timedelta(days=step_days)  # 变量赋值
