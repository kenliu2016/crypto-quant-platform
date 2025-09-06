# 内置策略一览（扩展）

- **GridTrading**：网格交易（对数价差阶梯 → 目标仓位），参数：`center_lookback, grid_step_bps, max_abs_exposure`
- **SimpleMaker**：被动做市的库存带控制（近似），参数：`halflife_vol, inventory_cap, kappa`
- **MomoLowVol**：动量 + 低波动双因子排名配仓，参数：`momo_lb, vol_hl, long_n, short_n, combo_alpha`
- **PairsCI**：均值回归配对（滚动 beta 模拟协整），参数：`pair_a, pair_b, lookback, z_entry, z_exit`

> 以上策略均实现 `BaseStrategy` 接口，输出 `target_weight`，可直接用于回测/调参/组合。对应的调参模板与示例运行脚本见 `configs/` 与 `examples/`。
