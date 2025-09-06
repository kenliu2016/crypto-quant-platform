from fastapi import FastAPI, Header, Request, HTTPException  # 引入依赖库
import os, hmac, hashlib, json  # 引入依赖库

SECRET = os.getenv("API_SECRET", "change-me")  # 变量赋值
app = FastAPI()  # 变量赋值

# 定义函数 verify_signature，实现具体功能逻辑
def verify_signature(body: bytes, signature: str):
    if not signature:  # 条件判断
        return False  # 返回结果
    mac = hmac.new(SECRET.encode(), msg=body, digestmod=hashlib.sha256).hexdigest()  # 变量赋值
    return hmac.compare_digest(mac, signature)  # 返回结果

@app.post("/pine/webhook")  # 函数调用
async def pine_webhook(request: Request, x_signature: str | None = Header(default=None)):  # 变量赋值
    body = await request.body()  # 变量赋值
    if not verify_signature(body, x_signature or ""):  # 条件判断
        raise HTTPException(status_code=401, detail="invalid signature")  # 变量赋值
    payload = await request.json()  # 变量赋值
    # expected: { "symbol": "BTCUSDT", "tw": 1.0, "note": "long", "ts": 1234567890 }
    # TODO: map to PineAdapterStrategy state or enqueue
    return {"ok": True}  # 返回结果
