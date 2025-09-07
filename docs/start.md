1. 进入项目根目录

假设解压后目录是：

cd /Users/aaronkliu/Documents/project/crypto-quant-platform

2. 激活 Python 环境

你之前用的是 pyenv，确认进入虚拟环境：

pyenv activate <你的环境名>


或者用 venv / conda：

source venv/bin/activate

3. 安装依赖
pip install -r requirements.txt


如果没有 requirements.txt，至少要装：

pip install streamlit sqlalchemy pandas numpy matplotlib

4. 启动 Streamlit

你有个 apps/cli.py（入口脚本），一般启动方式是：

streamlit run apps/cli.py


这样会启动本地服务（默认端口 8501），浏览器打开：

http://localhost:8501