import optuna  # 引入依赖库
from core.backtester import Backtester  # 引入依赖库

# 定义函数 build_objective，实现具体功能逻辑
def build_objective(base_cfg, space, objective_key = "sharpe"):  # 变量赋值
# 定义函数 objective，实现具体功能逻辑
    def objective(trial: optuna.Trial):
        cfg = dict(base_cfg)  # 变量赋值
        # sample
        for p in space:  # 循环遍历
            t = p.get("type")  # 变量赋值
            if t == "int":  # 条件判断
                cfg[p["name"]] = trial.suggest_int(p["name"], p["low"], p["high"])  # 变量赋值
            elif t == "float":
                cfg[p["name"]] = trial.suggest_float(p["name"], p["low"], p["high"], log=p.get("log", False))  # 变量赋值
            elif t == "cat":
                cfg[p["name"]] = trial.suggest_categorical(p["name"], p["choices"])  # 变量赋值
        result = Backtester(cfg).run()  # 变量赋值
        return float(result.metrics.get(objective_key, 0.0))  # 返回结果
    return objective  # 返回结果
