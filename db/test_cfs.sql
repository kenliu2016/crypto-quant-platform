-- ===========================================================
-- db/test_cfs.sql
-- 验证 cfs 用户是否有权限 SELECT / INSERT / DELETE
-- 适配 quant 库真实表结构
-- ===========================================================

-- 查看当前用户
SELECT current_user AS login_user;

-- 1. SELECT 测试（equity_curve）
SELECT * FROM equity_curve LIMIT 3;

-- 2. 获取一个已有的 run_id（用于后续插入测试）
--    注意：这里取最新的一个 run_id
\set test_run_id `psql -U cfs -d quant -Atc "SELECT run_id FROM run ORDER BY started_at DESC LIMIT 1;"`

-- 显示 run_id
SELECT :'test_run_id' AS test_run_id;

-- 3. INSERT/DELETE 测试（positions 表）
-- 插入一条测试记录
INSERT INTO positions (run_id, datetime, code, qty, avg_price)
VALUES (:'test_run_id', now(), 'TEST_CFS', 123.45, 100.00);

-- 查询刚插入的数据
SELECT * FROM positions WHERE code = 'TEST_CFS' ORDER BY datetime DESC LIMIT 1;

-- 删除测试数据
DELETE FROM positions WHERE code = 'TEST_CFS';

-- 4. INSERT/DELETE 测试（equity_curve 表）
INSERT INTO equity_curve (run_id, datetime, nav, drawdown)
VALUES (:'test_run_id', now(), 1000000.0, 0.0);

-- 查询刚插入的数据
SELECT * FROM equity_curve WHERE run_id = :'test_run_id' ORDER BY datetime DESC LIMIT 1;

-- 删除测试数据
DELETE FROM equity_curve WHERE run_id = :'test_run_id' AND nav = 1000000.0;
