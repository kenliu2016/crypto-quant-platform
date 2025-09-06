# 功能描述（最全）

## 平台能力
- 策略即插件，统一 `BaseStrategy` 协议；策略/数据/撮合/风控/优化器/报告均可插拔。
- 数据：Postgres + 适配器（Binance 1m）。
- 回测：事件驱动，目标权重/离散信号两种路径；撮合含费率/滑点；PortfolioTracker 持仓与净值跟踪。
- 调参：Optuna（Bayes/TPE）；Walk-Forward；目标函数可选 Sharpe/Calmar/IC/命中率。
- 评估：年化、波动、夏普、Sortino、回撤、卡玛、胜率、盈亏比、换手等。
- 报告：Streamlit 报表 + 导出 PDF/Excel；落库 `metrics/equity_curve`。
- Webhook：TradingView Pine Alert → FastAPI 接收 → 策略插件映射 → 入队执行。
- Dashboard：Backtest 一键落库/报告、多 run 对比；Tuning；Batch 生成器；进度跟踪；通知配置。
- 通知：回测/调参完成发送 Email/Slack/钉钉。
- 扩展：新增策略只需实现 `BaseStrategy` 并注册。

## 数据流
`DataAdapter` → `Backtester`(事件驱动) → `BrokerSim`(撮合) → `PortfolioTracker` → `metrics`/`equity_curve` → DB → Streamlit 可视化/导出报告。

## 统一接口（精简）
- BaseStrategy.parameters(): 参数空间声明
- BaseStrategy.prepare(data, meta)
- BaseStrategy.generate_signals(bar, state) → {target_weight|signal}
- PortfolioTracker: 跟踪现金/持仓/净值/回撤/夏普
- TradingView Webhook 适配：JSON → 归一化信号 → 策略插件 `PineAdapterStrategy` 消化


## 内置策略清单（新增）
- SMACross：经典双均线 + 波动率目标
- Donchian：唐奇安通道突破 + ATR 风险
- RSI_BBands：RSI + 布林带均值回归
- MACD：MACD 趋势跟随
- XSecMomentum：横截面动量（TopN/BottomN 多空）
- VolTarget：波动率目标等权配置（风险平价近似）
- BreakoutPullback：突破后回撤介入


## 内置策略清单（扩展新增）
- GridTrading：网格交易，围绕均值分层挂单
- MarketMaking：被动做市，价差管理
- MomentumVol：动量+波动率双因子选币
- PairsTrading：协整配对均值回归
