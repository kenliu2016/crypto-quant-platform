import pandas as pd
from typing import Dict, Any
from .portfolio_tracker import PortfolioTracker
from .broker import BrokerSim
from core import db  # ✅ 使用项目内已有的 db.py

class Backtester:
    def __init__(self, cfg: Dict[str, Any]):
        self.cfg = cfg
        self.tracker = PortfolioTracker(init_cash=cfg.get("init_cash", 100000.0))
        self.broker = BrokerSim(
            fee=cfg.get("cost", {}).get("fee", 0.001),
            slippage=cfg.get("cost", {}).get("slippage", 0.0005),
            tracker=self.tracker
        )

    def load_data(self) -> pd.DataFrame:
        codes = self.cfg.get("universe", ["000001.SZ"])
        start = self.cfg.get("start", "2023-01-01")
        end = self.cfg.get("end", "2023-12-31")

        query = f"""
        SELECT datetime, code, open, high, low, close, volume
        FROM minute_realtime
        WHERE code IN ({','.join([f"'{c}'" for c in codes])})
          AND datetime BETWEEN '{start}' AND '{end}'
        ORDER BY datetime ASC
        """
        engine = db.get_engine()
        data = pd.read_sql(query, engine, parse_dates=["datetime"])
        data = data.set_index(["datetime", "code"]).sort_index()
        data = data.dropna(subset=["close"])  # ⚠️ 删除缺少收盘价的行
        return data

    def run(self):
        data = self.load_data()
        codes = self.cfg.get("universe")
        if not codes:
            codes = data.index.get_level_values("code").unique().tolist()

        tw = pd.Series(1.0 / len(codes), index=codes)

        for dt, frame in data.groupby(level=0):
            prices = frame["close"].droplevel(1)
            if len(self.tracker.nav) == 0:
                self.broker.place_target_weights(dt, tw, prices)
            self.tracker.mark_to_market(dt, prices)
            self.tracker.snapshot_drawdown()

        equity_df = pd.DataFrame(self.tracker.nav, columns=["datetime", "nav"]).set_index("datetime")
        dd = pd.Series(self.tracker.dd, index=equity_df.index, name="drawdown")
        metrics = self.tracker.metrics()
        return type("Result", (), {
            "metrics": metrics,
            "equity_curve": equity_df.join(dd),
            "report_path": "#", "artifacts": {}
        })
