import optuna, json  # 引入依赖库
from .objective import build_objective  # 引入依赖库

# 定义函数 run_study，实现具体功能逻辑
def run_study(base_cfg, space, n_trials=30, objective_key="sharpe"):  # 变量赋值
    study = optuna.create_study(direction="maximize")  # 变量赋值
    study.optimize(build_objective(base_cfg, space, objective_key), n_trials=n_trials)  # 变量赋值
    return study  # 返回结果
