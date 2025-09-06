import sys
import os

# ========= 自动加入项目根目录到 sys.path =========
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))      # apps/pages/
ROOT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))      # crypto-quant-platform/
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

import streamlit as st  # 引入依赖库
import yaml, os, requests, smtplib  # 引入依赖库
from email.mime.text import MIMEText  # 引入依赖库

CONFIG_FILE = "configs/notify.yaml"  # 变量赋值

# 定义函数 load_notify_config，实现具体功能逻辑
def load_notify_config():
    if os.path.exists(CONFIG_FILE):  # 条件判断
        return yaml.safe_load(open(CONFIG_FILE, "r"))  # 返回结果
    return {}  # 返回结果

# 定义函数 save_notify_config，实现具体功能逻辑
def save_notify_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        yaml.safe_dump(cfg, f)  # 函数调用

# 定义函数 send_email，实现具体功能逻辑
def send_email(subject, body, cfg):
    msg = MIMEText(body, "plain", "utf-8")  # 变量赋值
    msg["Subject"] = subject  # 变量赋值
    msg["From"] = cfg["smtp_user"]  # 变量赋值
    msg["To"] = cfg["email"]  # 变量赋值
    with smtplib.SMTP_SSL(cfg["smtp_host"], cfg["smtp_port"]) as server:
        server.login(cfg["smtp_user"], cfg["smtp_pass"])  # 函数调用
        server.sendmail(cfg["smtp_user"], [cfg["email"]], msg.as_string())  # 函数调用

# 定义函数 send_slack，实现具体功能逻辑
def send_slack(msg, webhook_url):
    requests.post(webhook_url, json={"text": msg})  # 变量赋值

# 定义函数 send_dingtalk，实现具体功能逻辑
def send_dingtalk(msg, webhook_url):
    requests.post(webhook_url, json={"msgtype":"text","text":{"content":msg}})  # 变量赋值

st.title("🔔 通知配置")  # 函数调用
cfg = load_notify_config()  # 变量赋值
notify_type = st.selectbox("选择通知方式", ["none","email","slack","dingtalk"], index=["none","email","slack","dingtalk"].index(cfg.get("type","none")))  # 变量赋值
new_cfg = {"type": notify_type}  # 变量赋值
if notify_type=="email":  # 条件判断
    new_cfg["email"] = st.text_input("收件邮箱", cfg.get("email",""))  # 变量赋值
    new_cfg["smtp_host"] = st.text_input("SMTP Host", cfg.get("smtp_host","smtp.gmail.com"))  # 变量赋值
    new_cfg["smtp_port"] = st.number_input("SMTP Port", value=cfg.get("smtp_port",465))  # 变量赋值
    new_cfg["smtp_user"] = st.text_input("SMTP 用户", cfg.get("smtp_user",""))  # 变量赋值
    new_cfg["smtp_pass"] = st.text_input("SMTP 密码/授权码", type="password", value=cfg.get("smtp_pass",""))  # 变量赋值
elif notify_type=="slack":
    new_cfg["slack_webhook"] = st.text_input("Slack Webhook URL", cfg.get("slack_webhook",""))  # 变量赋值
elif notify_type=="dingtalk":
    new_cfg["dingtalk_webhook"] = st.text_input("钉钉 Webhook URL", cfg.get("dingtalk_webhook",""))  # 变量赋值

if st.button("💾 保存配置"):  # 条件判断
    save_notify_config(new_cfg); st.success("已保存")  # 函数调用

if st.button("📨 发送测试通知"):  # 条件判断
    try:
        if notify_type=="email":  # 条件判断
            send_email("测试通知", "Hello from Quant Platform ✅", new_cfg)  # 函数调用
        elif notify_type=="slack":
            send_slack("测试通知：Hello from Quant Platform ✅", new_cfg["slack_webhook"])  # 函数调用
        elif notify_type=="dingtalk":
            send_dingtalk("测试通知：Hello from Quant Platform ✅", new_cfg["dingtalk_webhook"])  # 函数调用
        else:
            st.warning("未选择通知方式"); raise SystemExit
        st.success("测试通知已发送 ✅")  # 函数调用
    except Exception as e:
        st.error(f"发送失败: {e}")  # 函数调用
