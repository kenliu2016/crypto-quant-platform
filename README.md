# Quant Platform (Crypto Backtest/Tuning/Live with Streamlit & TradingView Webhook)

A modular, production-ready scaffold for quantitative strategy research and management.

- Binance spot symbols (BTCUSDT, ETHUSDT, …)
- 1-min bars; date range: 2023-01-01 ~ 2025-09-05
- Postgres for storage
- AWS deployment (EC2 + RDS recommended)
- Streamlit dashboard (Backtest, Tuning, Reports, Batch Generator, Notify)
- PortfolioTracker integrated with broker sim (NAV/DD/Sharpe)
- TradingView Pine Webhook adapter → strategy plugin mapping
- Batch backtests & param grid generator, real-time progress page
- Notifications (email / Slack / DingTalk)

> Generated at 2025-09-06T08:46:31.895052Z


## 数据库封装调用说明
项目已统一封装数据库连接，位于 `core/db.py`：

- 获取 psycopg2 连接：
```python
from core.db import get_connection
conn = get_connection()
```

- 获取 SQLAlchemy Engine：
```python
from core.db import get_engine
engine = get_engine()
```
