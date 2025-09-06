-- db/create_user_cfs.sql
-- ======================================
-- 创建新用户 cfs，并授予 quant 数据库权限
-- ======================================

-- 1. 创建用户 cfs（密码：Aa520@cfs）
CREATE USER cfs WITH PASSWORD 'Aa520@cfs';

-- 2. 授予数据库 quant 的连接权限
GRANT CONNECT ON DATABASE quant TO cfs;

-- 3. 切换到 quant 数据库（执行时需手动 \c quant）
-- 在 psql 里执行： \c quant

-- 4. 授予 public schema 的使用权限
GRANT USAGE ON SCHEMA public TO cfs;

-- 5. 授予 cfs 用户对 public schema 下所有已有表和索引的操作权限
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO cfs;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO cfs;

-- 6. 确保以后新建的表、索引默认也给 cfs 权限
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO cfs;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT ALL PRIVILEGES ON SEQUENCES TO cfs;