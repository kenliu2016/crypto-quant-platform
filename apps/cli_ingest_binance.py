import argparse
import time
import datetime
from binance.client import Client
from sqlalchemy import text
from core.db import get_engine
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import logging
import os

# ----------------- 日志配置 -----------------
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "binance_ingest.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
# -------------------------------------------

# Binance API 初始化（拉取公开数据可不填 key/secret）
api_key = ""
api_secret = ""
client = Client(api_key, api_secret)


def save_batch_to_db(batch, symbol, table="minute_realtime"):
    """将一批K线数据保存到数据库"""
    if not batch:
        return

    engine = get_engine()
    with engine.begin() as conn:
        for row in batch:
            sql = text(f"""
                INSERT INTO {table} (datetime, code, open, high, low, close, volume)
                VALUES (:datetime, :code, :open, :high, :low, :close, :volume)
                ON CONFLICT (datetime, code) DO NOTHING
            """)
            conn.execute(sql, {
                "datetime": datetime.datetime.fromtimestamp(row[0]/1000),
                "code": symbol,
                "open": float(row[1]),
                "high": float(row[2]),
                "low": float(row[3]),
                "close": float(row[4]),
                "volume": float(row[5])
            })


def fetch_and_save(symbol, interval, start, end, max_retries=3):
    """循环分页拉取 Binance 历史K线，并逐批保存到数据库"""
    limit = 1000
    current = start
    total_saved = 0
    retries = 0

    engine = get_engine()

    while True:
        try:
            data = client.get_klines(
                symbol=symbol,
                interval=interval,
                startTime=current,
                endTime=end,
                limit=limit
            )
        except Exception as e:
            retries += 1
            if retries > max_retries:
                msg = f"{symbol}: 获取数据失败，已重试 {max_retries} 次: {e}"
                logger.error(msg)
                raise RuntimeError(msg)
            logger.warning(f"{symbol}: 获取数据失败，重试中 ({retries}/{max_retries}) ... {e}")
            time.sleep(1)
            continue

        if not data:
            break

        # 保存本批数据
        save_batch_to_db(data, symbol)
        total_saved += len(data)
        logger.info(f"{symbol}: 已保存累计 {total_saved} 条记录")

        # 更新游标 → 最后一根K线的时间 + 1ms
        last_open_time = data[-1][0]
        current = last_open_time + 1

        # 避免 API 限速
        time.sleep(0.2)

        # 如果不足 1000 条，说明已经取完
        if len(data) < limit:
            break

    return f"✅ {symbol}: 拉取完成，累计保存 {total_saved} 条记录"


def get_last_timestamp(symbol, table="minute_realtime"):
    """查数据库里已有的最新时间"""
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(
            text(f"SELECT MAX(datetime) FROM {table} WHERE code=:code"),
            {"code": symbol}
        ).scalar()
    return result


def run_task(symbol, interval, start_ts, end_ts, force):
    """执行单币种拉取任务"""
    last_time = get_last_timestamp(symbol)
    if not force and last_time and (not start_ts or last_time.timestamp() * 1000 > start_ts):
        start_ts = int(last_time.timestamp() * 1000) + 60_000
        logger.info(f"{symbol}: 从数据库已有记录之后继续拉取: {datetime.datetime.fromtimestamp(start_ts/1000)}")

    logger.info(f"{symbol}: 开始拉取 {interval} K线")
    return fetch_and_save(symbol, interval, start_ts, end_ts)


def main():
    parser = argparse.ArgumentParser(description="Binance 数据拉取器（边拉边存，支持并发+日志）")
    parser.add_argument("--symbols", type=str, default="BTCUSDT", 
                        help="交易对列表，用逗号分隔，如 BTCUSDT,ETHUSDT")
    parser.add_argument("--interval", type=str, default="1m", help="K线周期，如 1m/5m/1h")
    parser.add_argument("--start", type=str, default=None, help="起始日期，如 2023-01-01")
    parser.add_argument("--end", type=str, default=None, help="结束日期，如 2023-02-01")
    parser.add_argument("--force", action="store_true", help="忽略数据库已有数据，强制从 start 开始拉取")
    parser.add_argument("--workers", type=int, default=3, help="并发线程数")
    args = parser.parse_args()

    # 起始、结束时间戳
    start_ts = int(datetime.datetime.fromisoformat(args.start).timestamp() * 1000) if args.start else None
    end_ts = int(datetime.datetime.fromisoformat(args.end).timestamp() * 1000) if args.end else None

    # 支持批量任务
    symbols = [s.strip().upper() for s in args.symbols.split(",")]

    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(run_task, sym, args.interval, start_ts, end_ts, args.force): sym for sym in symbols}

        # tqdm 进度条
        for future in tqdm(as_completed(futures), total=len(futures), desc="任务进度"):
            sym = futures[future]
            try:
                msg = future.result()
                results.append(msg)
            except Exception as e:
                err = f"❌ {sym} 拉取失败: {e}"
                logger.error(err)
                results.append(err)

    # 输出结果
    print("\n--- 执行结果 ---")
    for r in results:
        print(r)


if __name__ == "__main__":
    main()
