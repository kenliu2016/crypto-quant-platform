-- ==========================================================
-- 内置策略初始化脚本
-- ==========================================================
-- 功能: 在 strategies 表中插入常见的量化交易策略
-- 注意: 需在 schema.sql 初始化完成后执行
--       psql -U postgres -h localhost -d quant -f db/init_strategies.sql
-- ==========================================================

-- 删除旧记录，避免重复插入
TRUNCATE TABLE strategies RESTART IDENTITY CASCADE;

-- ==============================
-- 1. 时间序列动量 (双均线策略)
-- ==============================
INSERT INTO strategies (name, description, params)
VALUES (
  'ts_momentum',
  '时间序列动量策略：使用快慢均线交叉信号进行交易',
  '{
    "ma_fast": 10,
    "ma_slow": 50,
    "target_risk": 0.02
  }'
);

-- ==============================
-- 2. 均值回归 (布林带)
-- ==============================
INSERT INTO strategies (name, description, params)
VALUES (
  'mean_reversion',
  '均值回归策略：基于布林带上下轨进行开仓/平仓',
  '{
    "lookback": 20,
    "num_std": 2,
    "stop_loss": 0.03
  }'
);

-- ==============================
-- 3. 网格交易 (Grid Trading)
-- ==============================
INSERT INTO strategies (name, description, params)
VALUES (
  'grid_trading',
  '网格交易策略：在价格区间内布置买卖挂单，低买高卖',
  '{
    "grid_size": 10,
    "grid_spacing": 0.005,
    "base_qty": 0.01
  }'
);

-- ==============================
-- 4. 做市策略 (被动挂单)
-- ==============================
INSERT INTO strategies (name, description, params)
VALUES (
  'market_making',
  '被动做市策略：在买一/卖一价附近挂单，赚取价差',
  '{
    "spread": 0.002,
    "order_size": 0.01,
    "inventory_limit": 1.0
  }'
);

-- ==============================
-- 5. 双因子 (动量 + 波动率)
-- ==============================
INSERT INTO strategies (name, description, params)
VALUES (
  'mom_vol_factor',
  '双因子策略：综合动量与波动率因子进行打分排序',
  '{
    "lookback_mom": 60,
    "lookback_vol": 30,
    "top_n": 5
  }'
);

-- ==============================
-- 6. 均值回归配对 (协整)
-- ==============================
INSERT INTO strategies (name, description, params)
VALUES (
  'pair_trading',
  '均值回归配对交易：基于协整检验和价差zscore进行开仓',
  '{
    "lookback": 120,
    "entry_z": 2.0,
    "exit_z": 0.5
  }'
);

-- ==============================
-- 7. 机器学习分类 (XGBoost)
-- ==============================
INSERT INTO strategies (name, description, params)
VALUES (
  'ml_classifier',
  '机器学习分类策略：使用XGBoost预测未来价格方向',
  '{
    "features": ["rsi", "macd", "volume_change"],
    "train_window": 500,
    "threshold": 0.55
  }'
);

-- ==========================================================
-- ✅ 内置策略初始化完成
-- ==========================================================