# 策略说明文档

本文件详细介绍了平台内置的量化交易策略，包括逻辑、适用场景、参数说明、调参建议以及示例配置。

---

## 策略对比表

| 策略类别 | 风险特征 | 适用市场/场景 | 典型指标 |
|----------|----------|---------------|-----------|
| 时间序列动量 | 趋势跟随，高回撤 | 趋势行情，BTC/ETH 等主流币 | 夏普率、卡玛比 |
| 横截面动量 | 多空对冲，中性 | 多品种组合，分散风险 | IC、RankIC、胜率 |
| 均值回归（布林/配对） | 高频交易，均值回归 | 区间震荡市场，协整资产对 | 盈亏比、胜率 |
| 因子多空 | 多因子组合，中风险 | 中长期投资，风格暴露 | 夏普、因子 IC |
| 机器学习分类/回归 | 依赖训练数据 | 特征充分，需回测验证 | AUC、F1、命中率 |
| 网格交易 | 稳健，低波动 | 震荡行情，USDT 交易对 | 总收益、回撤 |
| 做市（被动挂单） | 稳定收手续费，高资金需求 | 流动性较高的币对 | 手续费收入、换手率 |
| 动量+波动率双因子 | 趋势+防御 | 大类资产配置，择优筛选 | 夏普、波动率、回撤 |

---

## 策略说明

### 1. 时间序列动量（双均线/突破）

- **逻辑**：根据快/慢均线或价格突破生成趋势跟随信号。
- **适用场景**：趋势行情明显的币种（BTC、ETH）。
- **主要参数**：
  - `ma_fast`: 快速均线窗口
  - `ma_slow`: 慢速均线窗口
  - `target_risk`: 仓位风险目标
- **调参建议**：`ma_fast` 取 5~20，`ma_slow` 取 50~200。
- **示例 YAML**：
```yaml
strategy:
  name: TSMA
  params:
    ma_fast: 10
    ma_slow: 60
    target_risk: 0.1
```

---

### 2. 横截面动量（排名多空）

- **逻辑**：按过去一段时间收益率排名，买入前 N，卖出后 N。
- **适用场景**：多品种（BTC/ETH/BNB/ADA）。
- **主要参数**：
  - `lookback`: 排名回溯窗口
  - `top_n`: 做多数量
  - `bottom_n`: 做空数量
- **调参建议**：适合多标的组合，常用 `lookback=20`，`top_n=3`。
- **示例 YAML**：
```yaml
strategy:
  name: CrossSectionMomentum
  params:
    lookback: 20
    top_n: 3
    bottom_n: 3
```

---

### 3. 均值回归（布林带/配对协整）

- **逻辑**：价格偏离布林带或协整残差过大时建仓，回归均值时平仓。
- **适用场景**：震荡区间行情，协整币对（如 ETH/BTC）。
- **主要参数**：
  - `lookback`: 布林带窗口
  - `num_std`: 标准差阈值
  - `pair`: 配对币对（如 ETH-BTC）
- **调参建议**：`num_std` 一般取 2。
- **示例 YAML**：
```yaml
strategy:
  name: PairMeanReversion
  params:
    lookback: 20
    num_std: 2
    pair: ["ETH", "BTC"]
```

---

### 4. 因子多空

- **逻辑**：构建多因子打分，选优买入，差卖空。
- **适用场景**：中长期投资组合。
- **主要参数**：
  - `factors`: 动量、波动率、流动性等
  - `top_pct`: 做多比例
  - `bottom_pct`: 做空比例
- **调参建议**：适合稳定回测，验证因子有效性。
- **示例 YAML**：
```yaml
strategy:
  name: FactorLongShort
  params:
    factors: ["momentum", "volatility"]
    top_pct: 0.2
    bottom_pct: 0.2
```

---

### 5. 机器学习策略

- **逻辑**：通过 ML 模型预测未来收益/方向，转化为信号。
- **适用场景**：特征数据充分的情况。
- **主要参数**：
  - `model_type`: xgboost/lightgbm/logit
  - `lookback`: 特征窗口
  - `horizon`: 预测步长
- **调参建议**：需配合 Walk-Forward 验证。
- **示例 YAML**：
```yaml
strategy:
  name: MLClassifier
  params:
    model_type: xgboost
    lookback: 30
    horizon: 5
```

---

### 6. 网格交易

- **逻辑**：在设定的区间内分层挂单，低买高卖。
- **适用场景**：震荡行情。
- **主要参数**：
  - `grid_size`: 网格数量
  - `lower_bound`: 下限价格
  - `upper_bound`: 上限价格
- **调参建议**：网格数量过少无法覆盖行情，过多手续费高。
- **示例 YAML**：
```yaml
strategy:
  name: GridTrading
  params:
    grid_size: 10
    lower_bound: 1800
    upper_bound: 2200
```

---

### 7. 做市（被动挂单）

- **逻辑**：在买一/卖一价挂单赚取点差。
- **适用场景**：高流动性币对。
- **主要参数**：
  - `spread`: 挂单点差
  - `inventory_limit`: 库存限制
- **调参建议**：适合稳定手续费收入，需控制风险。
- **示例 YAML**：
```yaml
strategy:
  name: SimpleMaker
  params:
    spread: 0.001
    inventory_limit: 5
```

---

### 8. 动量+波动率双因子

- **逻辑**：同时考虑动量强度和低波动优势。
- **适用场景**：择优筛选标的。
- **主要参数**：
  - `lookback`: 回溯窗口
  - `top_n`: 选择数量
- **调参建议**：`lookback=60` 效果较好。
- **示例 YAML**：
```yaml
strategy:
  name: MomoLowVol
  params:
    lookback: 60
    top_n: 5
```

---

# 使用方法

1. 在 `configs/strategy.xxx.yaml` 中定义参数。  
2. 在 Streamlit 仪表盘选择策略 + 配置运行。  
3. 回测完成后，可导出 PDF/Excel 报告，或对比多个 run。  
