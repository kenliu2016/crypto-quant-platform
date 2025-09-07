# 用户使用手册

## 快速开始
1. 配置 `configs/datasource.yaml` 与 Postgres 连接。
2. 启动 Streamlit 仪表盘：Home → Backtest → 选择策略、标的池、区间 → 运行回测并写库。
3. Reports 页查看净值曲线、回撤、指标；导出 PDF/Excel。
4. BatchGenerator 生成网格参数批量任务，一键提交队列。
5. Notify 设置通知方式，发送测试消息。
6. TradingView：将 Pine Alert 指向 `/api/pine/webhook`，使用文档中的 JSON 模板。

## Backtest 页
- 自动写库、打开报告、多 run 对比、成交分布对比、参数复现。

## Tuning 页
- 选择目标函数/窗口；查看最优 trial 与敏感性图。

## 进度跟踪
- 实时刷新、筛选状态、夏普榜单、勾选多任务 overlay。

## 故障排查
- 查看 `run` 表的 `status/notes`
- 检查 Webhook server 日志与 API_SECRET



# binance 数据适配器

# 只拉取历史数据
python -m apps.cli_ingest --rest-only

# 只启动实时订阅
python -m apps.cli_ingest --ws-only

# 先拉历史再接实时
python -m apps.cli_ingest



# Binance 数据适配器用法示例
1. 批量并发拉取多个交易对
python -m apps.cli_ingest_binance --symbols BTCUSDT,ETHUSDT,BNBUSDT --interval 1m --start 2023-01-01 --end 2025-09-06 --force --workers 3

这里 --workers 3 表示同时开 3 个线程，分别拉不同交易对。

2. 单币对（默认 1 个线程）
python -m apps.cli_ingest_binance --symbols BTCUSDT --interval 5m --start 2023-01-01 --end 2023-01-10 --force

