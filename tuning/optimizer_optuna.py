import optuna  # 引入依赖库

# 定义函数 suggest_params，实现具体功能逻辑
def suggest_params(trial, space):
    cfg = {}  # 变量赋值
    for p in space:  # 循环遍历
        t = p.get("type")  # 变量赋值
        if t == "int":  # 条件判断
            cfg[p["name"]] = trial.suggest_int(p["name"], p["low"], p["high"])  # 变量赋值
        elif t == "float":
            cfg[p["name"]] = trial.suggest_float(p["name"], p["low"], p["high"], log=p.get("log", False))  # 变量赋值
        elif t == "cat":
            cfg[p["name"]] = trial.suggest_categorical(p["name"], p["choices"])  # 变量赋值
    return cfg  # 返回结果
