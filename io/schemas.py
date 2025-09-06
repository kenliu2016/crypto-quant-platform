from sqlalchemy.orm import declarative_base, Mapped, mapped_column  # 引入依赖库
from sqlalchemy import String, Integer, Float, JSON, TIMESTAMP, ForeignKey  # 引入依赖库
import uuid  # 引入依赖库

Base = declarative_base()  # 变量赋值

# 定义类 Run，用于封装相关逻辑或功能模块
class Run(Base):
    __tablename__ = "run"  # 变量赋值
    run_id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))  # 变量赋值
    run_type: Mapped[str] = mapped_column(String(16))  # 变量赋值
    strategy_id: Mapped[int] = mapped_column(Integer)  # 变量赋值
    config: Mapped[dict] = mapped_column(JSON)  # 变量赋值
    code_version: Mapped[str] = mapped_column(String(64), default="v1")  # 变量赋值
    started_at: Mapped[str] = mapped_column(TIMESTAMP)  # 变量赋值
    ended_at: Mapped[str] = mapped_column(TIMESTAMP, nullable=True)  # 变量赋值
    status: Mapped[str] = mapped_column(String(16), default="done")  # 变量赋值
    notes: Mapped[str] = mapped_column(String, nullable=True)  # 变量赋值

# 定义类 Metrics，用于封装相关逻辑或功能模块
class Metrics(Base):
    __tablename__ = "metrics"  # 变量赋值
    run_id: Mapped[str] = mapped_column(String, ForeignKey("run.run_id"), primary_key=True)  # 变量赋值
    metric_name: Mapped[str] = mapped_column(String(64), primary_key=True)  # 变量赋值
    metric_value: Mapped[float] = mapped_column(Float)  # 变量赋值

# 定义类 Reports，用于封装相关逻辑或功能模块
class Reports(Base):
    __tablename__ = "reports"  # 变量赋值
    run_id: Mapped[str] = mapped_column(String, ForeignKey("run.run_id"), primary_key=True)  # 变量赋值
    report_path: Mapped[str] = mapped_column(String(256))  # 变量赋值
    artifact_paths: Mapped[dict] = mapped_column(JSON)  # 变量赋值

# 定义类 EquityCurve，用于封装相关逻辑或功能模块
class EquityCurve(Base):
    __tablename__ = "equity_curve"  # 变量赋值
    run_id: Mapped[str] = mapped_column(String, ForeignKey("run.run_id"), primary_key=True)  # 变量赋值
    datetime: Mapped[str] = mapped_column(TIMESTAMP, primary_key=True)  # 变量赋值
    nav: Mapped[float] = mapped_column(Float)  # 变量赋值
    drawdown: Mapped[float] = mapped_column(Float)  # 变量赋值

# 定义类 Orders，用于封装相关逻辑或功能模块
class Orders(Base):
    __tablename__ = "orders"  # 变量赋值
    run_id: Mapped[str] = mapped_column(String, ForeignKey("run.run_id"), primary_key=True)  # 变量赋值
    datetime: Mapped[str] = mapped_column(TIMESTAMP, primary_key=True)  # 变量赋值
    code: Mapped[str] = mapped_column(String(32), primary_key=True)  # 变量赋值
    side: Mapped[str] = mapped_column(String(4))  # 变量赋值
    qty: Mapped[float] = mapped_column(Float)  # 变量赋值
    price: Mapped[float] = mapped_column(Float)  # 变量赋值
    reason: Mapped[str] = mapped_column(String(64))  # 变量赋值

# 定义类 Fills，用于封装相关逻辑或功能模块
class Fills(Base):
    __tablename__ = "fills"  # 变量赋值
    run_id: Mapped[str] = mapped_column(String, ForeignKey("run.run_id"), primary_key=True)  # 变量赋值
    datetime: Mapped[str] = mapped_column(TIMESTAMP, primary_key=True)  # 变量赋值
    code: Mapped[str] = mapped_column(String(32), primary_key=True)  # 变量赋值
    side: Mapped[str] = mapped_column(String(4))  # 变量赋值
    qty: Mapped[float] = mapped_column(Float)  # 变量赋值
    price: Mapped[float] = mapped_column(Float)  # 变量赋值
    fee: Mapped[float] = mapped_column(Float)  # 变量赋值

# 定义类 Positions，用于封装相关逻辑或功能模块
class Positions(Base):
    __tablename__ = "positions"  # 变量赋值
    run_id: Mapped[str] = mapped_column(String, ForeignKey("run.run_id"), primary_key=True)  # 变量赋值
    datetime: Mapped[str] = mapped_column(TIMESTAMP, primary_key=True)  # 变量赋值
    code: Mapped[str] = mapped_column(String(32), primary_key=True)  # 变量赋值
    qty: Mapped[float] = mapped_column(Float)  # 变量赋值
    avg_price: Mapped[float] = mapped_column(Float)  # 变量赋值
