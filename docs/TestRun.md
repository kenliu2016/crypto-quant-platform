TestRun使用方法

进入项目根目录，运行：
streamlit run apps/pages/TestRun.py --server.port 8501
然后打开 http://localhost:8501 就能看到 TestRun 页面 🎉



test_run.py使用方法

先确保数据库表和内置策略都已创建：
psql -U postgres -h localhost -d quant -f db/schema.sql
psql -U postgres -h localhost -d quant -f db/init_strategies.sql
运行测试脚本（随机数据模拟回测）：
python apps/test_run.py --strategy ts_momentum --codes BTCUSDT ETHUSDT --start 2024-01-01 --end 2024-01-15
验证数据库内容：
psql -U postgres -h localhost -d quant -c "SELECT * FROM backtest_runs;"
psql -U postgres -h localhost -d quant -c "SELECT * FROM metrics;"
psql -U postgres -h localhost -d quant -c "SELECT * FROM equity_curve LIMIT 10;"


使用方法

在项目根目录运行：
python apps/run_dashboard.py
打开浏览器访问：
http://localhost:8501
即可进入 Streamlit 仪表盘，看到首页（Home 页面），从这里你可以跳转到 回测 / 调参 / 报告 / 测试运行 等页面。