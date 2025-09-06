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
