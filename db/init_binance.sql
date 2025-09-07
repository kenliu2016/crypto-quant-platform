-- Binance 实时/历史分钟行情表
CREATE TABLE IF NOT EXISTS minute_realtime (
  datetime TIMESTAMP NOT NULL,
  code     VARCHAR(32) NOT NULL,
  open     DOUBLE PRECISION NOT NULL,
  high    DOUBLE PRECISION NOT NULL,
  low      DOUBLE PRECISION NOT NULL,
  close    DOUBLE PRECISION NOT NULL,
  volume   DOUBLE PRECISION NOT NULL,
  PRIMARY KEY(datetime, code)
);
CREATE INDEX IF NOT EXISTS idx_minute_realtime_code_time
  ON minute_realtime(code, datetime);
