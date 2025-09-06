-- ==========================================================
-- 量化交易平台数据库初始化脚本
-- ==========================================================
-- 作者: ChatGPT (自动生成)
-- 功能: 初始化策略管理、回测、交易执行、指标等核心表
-- 注意: 在 PostgreSQL 中执行
--       psql -U postgres -h localhost -d quant -f db/schema.sql
-- ==========================================================

-- ======================
-- 策略注册表 (strategies)
-- ======================
-- 用于保存系统内置和用户自定义的策略
CREATE TABLE IF NOT EXISTS strategies (
    id SERIAL PRIMARY KEY,                  -- 策略唯一ID
    name TEXT UNIQUE NOT NULL,              -- 策略名称 (如 grid_trading)
    description TEXT,                       -- 策略描述
    params JSONB DEFAULT '{}'::jsonb,       -- 策略参数 (JSON 格式)
    created_at TIMESTAMP DEFAULT now()      -- 创建时间
);

-- ============================
-- 策略运行记录 (backtest_runs)
-- ============================
-- 保存回测 / 调参 / 实盘运行的元信息
CREATE TABLE IF NOT EXISTS backtest_runs (
    run_id UUID PRIMARY KEY,                -- 唯一运行ID
    strategy_id INT REFERENCES strategies(id),
    run_type TEXT NOT NULL,                 -- backtest / tuning / live
    config JSONB,                           -- 运行时配置参数
    code_version TEXT,                      -- 代码版本(Git Hash)
    started_at TIMESTAMP DEFAULT now(),
    ended_at TIMESTAMP,
    status TEXT,                            -- running / success / failed
    notes TEXT
);

-- ===================
-- 订单表 (orders)
-- ===================
-- 记录每次下单事件
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    run_id UUID REFERENCES backtest_runs(run_id),
    datetime TIMESTAMP NOT NULL,
    code TEXT NOT NULL,                     -- 交易标的 (BTC/ETH/股票代码)
    side TEXT NOT NULL,                     -- buy/sell
    qty DOUBLE PRECISION NOT NULL,          -- 下单数量
    price DOUBLE PRECISION NOT NULL,        -- 下单价格
    reason TEXT                             -- 信号来源 (如 策略触发/止损)
);

-- ===================
-- 成交表 (trades)
-- ===================
-- 记录每次撮合成交
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    run_id UUID REFERENCES backtest_runs(run_id),
    datetime TIMESTAMP NOT NULL,
    code TEXT NOT NULL,
    side TEXT NOT NULL,                     -- buy/sell
    qty DOUBLE PRECISION NOT NULL,          -- 成交数量
    price DOUBLE PRECISION NOT NULL,        -- 成交价格
    fee DOUBLE PRECISION DEFAULT 0.0        -- 手续费
);

-- ===================
-- 持仓表 (positions)
-- ===================
-- 记录持仓变化 (逐时刻更新)
CREATE TABLE IF NOT EXISTS positions (
    id SERIAL PRIMARY KEY,
    run_id UUID REFERENCES backtest_runs(run_id),
    datetime TIMESTAMP NOT NULL,
    code TEXT NOT NULL,
    qty DOUBLE PRECISION NOT NULL,          -- 当前持仓量
    avg_price DOUBLE PRECISION NOT NULL     -- 平均持仓成本
);

-- ===================
-- 指标表 (metrics)
-- ===================
-- 保存运行结果的核心指标 (Sharpe, Calmar, WinRate 等)
CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    run_id UUID REFERENCES backtest_runs(run_id),
    metric_name TEXT NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL
);

-- ==========================
-- 净值曲线表 (equity_curve)
-- ==========================
-- 记录每个时间点的净值和风险指标
CREATE TABLE IF NOT EXISTS equity_curve (
    id SERIAL PRIMARY KEY,
    run_id UUID REFERENCES backtest_runs(run_id),
    datetime TIMESTAMP NOT NULL,
    nav DOUBLE PRECISION NOT NULL,          -- 净值
    drawdown DOUBLE PRECISION NOT NULL      -- 回撤
);

-- ==========================
-- 报告索引表 (reports)
-- ==========================
-- 记录生成的报告路径 (HTML/PDF/Excel)
CREATE TABLE IF NOT EXISTS reports (
    run_id UUID REFERENCES backtest_runs(run_id) PRIMARY KEY,
    report_path TEXT,                       -- 报告文件路径
    artifact_paths JSONB                    -- 相关工件 (图表/CSV/因子暴露等)
);

-- ==========================================================
-- ✅ 所有表已定义完成
-- ==========================================================