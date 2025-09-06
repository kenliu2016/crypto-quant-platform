-- Postgres schema (complete)

CREATE TABLE IF NOT EXISTS strategy_registry (
  strategy_id SERIAL PRIMARY KEY,
  name VARCHAR(128) NOT NULL,
  version VARCHAR(32) NOT NULL,
  entry_file VARCHAR(256) NOT NULL,
  class_name VARCHAR(128) NOT NULL,
  UNIQUE(name, version)
);

CREATE TABLE IF NOT EXISTS strategy_params (
  strategy_id INT REFERENCES strategy_registry(strategy_id),
  param_name VARCHAR(64),
  type VARCHAR(16),
  low DOUBLE PRECISION,
  high DOUBLE PRECISION,
  choices JSONB,
  default_value JSONB,
  PRIMARY KEY(strategy_id, param_name)
);

CREATE TABLE IF NOT EXISTS run (
  run_id UUID PRIMARY KEY,
  run_type VARCHAR(16),
  strategy_id INT REFERENCES strategy_registry(strategy_id),
  config JSONB,
  code_version VARCHAR(64),
  started_at TIMESTAMP DEFAULT now(),
  ended_at TIMESTAMP,
  status VARCHAR(16),
  notes TEXT
);

CREATE TABLE IF NOT EXISTS metrics (
  run_id UUID REFERENCES run(run_id),
  metric_name VARCHAR(64),
  metric_value DOUBLE PRECISION,
  PRIMARY KEY(run_id, metric_name)
);

CREATE TABLE IF NOT EXISTS orders (
  run_id UUID REFERENCES run(run_id),
  datetime TIMESTAMP, code VARCHAR(32), side VARCHAR(4), qty DOUBLE PRECISION,
  price DOUBLE PRECISION, reason VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS fills (
  run_id UUID REFERENCES run(run_id),
  datetime TIMESTAMP, code VARCHAR(32), side VARCHAR(4), qty DOUBLE PRECISION,
  price DOUBLE PRECISION, fee DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS positions (
  run_id UUID REFERENCES run(run_id),
  datetime TIMESTAMP, code VARCHAR(32), qty DOUBLE PRECISION, avg_price DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS equity_curve (
  run_id UUID REFERENCES run(run_id),
  datetime TIMESTAMP, nav DOUBLE PRECISION, drawdown DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS reports (
  run_id UUID REFERENCES run(run_id) PRIMARY KEY,
  report_path VARCHAR(256),
  artifact_paths JSONB
);

-- Webhook 消息原始入库（可选）
CREATE TABLE IF NOT EXISTS pine_webhook_log (
  id BIGSERIAL PRIMARY KEY,
  received_at TIMESTAMP DEFAULT now(),
  payload JSONB,
  signature VARCHAR(128),
  handled BOOLEAN DEFAULT FALSE,
  run_id UUID
);

-- 通知配置（可选：也可用 YAML）
CREATE TABLE IF NOT EXISTS notify_config (
  id SERIAL PRIMARY KEY,
  type VARCHAR(16) DEFAULT 'none',
  config JSONB
);
