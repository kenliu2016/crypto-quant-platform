-- ===============================================
-- 修改 quant 数据库 public schema 下所有表和序列的 owner
-- 新 owner: cfs
-- 使用方法: 在 psql 中用超级用户 (postgres) 或当前 owner 执行
--     psql -U postgres -d quant -f db/change_owner_to_cfs.sql
-- ===============================================

-- 切换到 quant 数据库（如果你在 psql 内）
-- \c quant postgres

-- 修改所有表的 owner
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT schemaname, tablename
        FROM pg_tables
        WHERE schemaname = 'public'
    LOOP
        EXECUTE format('ALTER TABLE %I.%I OWNER TO cfs;', r.schemaname, r.tablename);
    END LOOP;
END
$$;

-- 修改所有序列的 owner
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT sequence_schema, sequence_name
        FROM information_schema.sequences
        WHERE sequence_schema = 'public'
    LOOP
        EXECUTE format('ALTER SEQUENCE %I.%I OWNER TO cfs;', r.sequence_schema, r.sequence_name);
    END LOOP;
END
$$;

-- 修改所有视图的 owner
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT table_schema, table_name
        FROM information_schema.views
        WHERE table_schema = 'public'
    LOOP
        EXECUTE format('ALTER VIEW %I.%I OWNER TO cfs;', r.table_schema, r.table_name);
    END LOOP;
END
$$;
