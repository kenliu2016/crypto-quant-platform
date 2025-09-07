# apps/cli_ingest.py
# -*- coding: utf-8 -*-
"""
Binance 数据接入器
支持：
1. REST 历史数据拉取
2. WebSocket 实时订阅（支持保存模式：final/realtime）
"""

import sys
import os
import yaml
import time
import argparse
import asyncio
import json
import logging
from datetime import datetime
import websockets
from sqlalchemy import Table, Column, MetaData, DateTime, String, Float
from sqlalchemy.dialects.postgresql import insert

# 项目根目录加入 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_io.adapters.adapter_binance import BinanceAdapter
from core.db import get_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config(config_path):
    """加载 YAML 配置"""
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


# ------------------ WebSocket 管理类 ------------------
metadata = MetaData()
cn_minute_realtime = Table(
    "cn_minute_realtime", metadata,
    Column("datetime", DateTime, primary_key=True),
    Column("code", String, primary_key=True),
    Column("open", Float),
    Column("high", Float),
    Column("low", Float),
    Column("close", Float),
    Column("volume", Float),
)


class BinanceWS:
    def __init__(self, symbols, interval="1m", uri="wss://stream.binance.com:9443/ws", save_mode="final"):
        self.symbols = [s.lower() for s in symbols]
        self.interval = interval
        self.uri = uri
        self.save_mode = save_mode
        self.engine = get_engine()

    async def connect(self):
        """建立 WebSocket 连接并订阅"""
        stream_names = [f"{s}@kline_{self.interval}" for s in self.symbols]
        stream_url = f"{self.uri}/{'/'.join(stream_names)}"
        logger.info(f"[Binance WS] 连接: {stream_url}, 保存模式={self.save_mode}")

        async for ws in websockets.connect(stream_url, ping_interval=20, ping_timeout=20):
            try:
                async for msg in ws:
                    self.handle_message(msg)
            except Exception as e:
                logger.warning(f"[Binance WS] 出错: {e}，5秒后重连")
                await asyncio.sleep(5)
                continue

    def handle_message(self, msg):
        """处理消息并写入数据库"""
        data = json.loads(msg)
        if "k" not in data:
            return

        k = data["k"]

        # --- 保存模式控制 ---
        if self.save_mode == "final" and not k["x"]:
            # final 模式下只在收盘时保存
            return

        record = {
            "datetime": datetime.fromtimestamp(k["t"] / 1000),
            "code": k["s"],
            "open": float(k["o"]),
            "high": float(k["h"]),
            "low": float(k["l"]),
            "close": float(k["c"]),
            "volume": float(k["v"]),
        }

        with self.engine.begin() as conn:
            stmt = insert(cn_minute_realtime).values(record)
            stmt = stmt.on_conflict_do_update(
                index_elements=["datetime", "code"],
                set_=record
            )
            conn.execute(stmt)

        logger.info(f"[Binance WS] 保存: {record['code']} {record['datetime']} close={record['close']} ({self.save_mode})")


# ------------------ 主逻辑入口 ------------------
def main():
    parser = argparse.ArgumentParser(description="Binance 数据接入器")
    parser.add_argument("--rest-only", action="store_true", help="只执行 REST 历史数据拉取")
    parser.add_argument("--ws-only", action="store_true", help="只执行 WebSocket 实时订阅")
    args = parser.parse_args()

    # 加载配置文件
    config = load_config("configs/datasource.binance.yaml")
    binance_config = config.get("binance", {})

    # 初始化 REST Adapter
    adapter = BinanceAdapter(
        api_key=binance_config.get("api_key", ""),
        api_secret=binance_config.get("api_secret", "")
    )

    # REST 历史数据拉取
    if args.rest_only or (not args.rest_only and not args.ws_only):
        if binance_config.get("rest", {}).get("enabled", True):
            print("执行 REST 历史数据拉取...")
            rest_config = binance_config["rest"]
            symbols = rest_config.get("symbols", ["BTCUSDT", "ETHUSDT"])
            interval = rest_config.get("interval", "1m")
            limit = rest_config.get("limit", 1000)

            for symbol in symbols:
                print(f"拉取 {symbol} 的历史数据...")
                klines = adapter.fetch_klines(symbol=symbol, interval=interval, limit=limit)
                print(f"获取到 {len(klines)} 条数据，保存到数据库...")
                adapter.save_klines_to_db(klines=klines, code=symbol)
                print(f"{symbol} 的数据保存完成")
        else:
            print("REST 数据拉取已禁用")

    # WebSocket 实时订阅
    if args.ws_only or (not args.rest_only and not args.ws_only):
        if binance_config.get("websocket", {}).get("enabled", True):
            print("执行 WebSocket 实时订阅...")
            ws_config = binance_config["websocket"]
            symbols = ws_config.get("symbols", ["btcusdt", "ethusdt"])
            interval = ws_config.get("interval", "1m")
            save_mode = ws_config.get("save_mode", "final")  # 新增模式配置

            ws = BinanceWS(symbols=symbols, interval=interval, save_mode=save_mode)
            try:
                asyncio.run(ws.connect())
            except KeyboardInterrupt:
                print("程序已停止")
        else:
            print("WebSocket 订阅已禁用")


if __name__ == "__main__":
    main()
