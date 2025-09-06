# 部署指南（AWS）

## 架构建议
- EC2 (Ubuntu 22.04) 运行：Streamlit + FastAPI (uvicorn) + Worker（Celery/RQ 可选）
- RDS Postgres（或自管 Postgres on EC2）
- S3 用于报告/工件存储（可选）；CloudFront 分发
- Nginx 反向代理：/app (Streamlit) /api (FastAPI)；TLS 用 ACM/Certbot

## 步骤
1. **系统依赖**
   ```bash
   sudo apt update && sudo apt install -y python3-pip python3-venv nginx postgresql-client
   ```
2. **项目部署**
   ```bash
   git clone <your-repo> && cd quant-platform
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **数据库**
   - 创建数据库与用户；执行 `db/schema.sql`。
   ```bash
   psql "postgres://user:pass@host:5432/db" -f db/schema.sql
   ```
4. **环境变量/Secrets**
   - `STREAMLIT_SECRET_db_url="postgresql+psycopg2://user:pass@host:5432/db"`
   - `API_SECRET=change-me`（Webhook 认证用）
5. **运行**
   - Streamlit: `streamlit run apps/dashboard/Home.py --server.port 8501 --server.address 0.0.0.0`
   - FastAPI: `uvicorn apps.webhook.server:app --host 0.0.0.0 --port 8000`
6. **Nginx（示例片段）**
   ```nginx
   server {
     listen 80;
     server_name _;
     location /app/ { proxy_pass http://127.0.0.1:8501/; proxy_set_header Host $host; }
     location /api/ { proxy_pass http://127.0.0.1:8000/; proxy_set_header Host $host; }
   }
   ```
7. **后台服务（systemd）**：为 uvicorn/streamlit 写 service 保持常驻。

## 生产注意
- 打开 Postgres 连接池（SQLAlchemy pool_pre_ping）
- Streamlit 基础鉴权（Nginx Basic / OIDC）
- API 密钥校验 + 签名校验防止伪造 Webhook
