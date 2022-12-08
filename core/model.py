from optparse import Option
from typing import Optional
from sqlalchemy import Column, DECIMAL, String, BigInteger, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()


class RunnerPerformanceOrm(Base):
    __tablename__ = 'runner_performance'
    id = Column(BigInteger, primary_key=True)
    runner_domain = Column(String, unique=True, nullable=False)
    avg_last_48_hours = Column(DECIMAL, nullable=False)
    avg_last_24_hours = Column(DECIMAL, nullable=False)
    avg_last_6_hours = Column(DECIMAL, nullable=False)
    total_chains = Column(BigInteger, nullable=False)
    total_nodes = Column(BigInteger, nullable=False)
    tokens = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)


class RunnerPerformance(BaseModel):
    runner_domain: str
    total_last_48_hours: Optional[float]
    total_last_24_hours: Optional[float]
    total_last_6_hours: Optional[float]
    avg_last_48_hours: Optional[float]
    avg_last_24_hours: Optional[float]
    avg_last_6_hours: Optional[float]
    jailed_now: Optional[int]
    total_chains: Optional[int]
    total_nodes: Optional[int]
    total_balance: Optional[float]
    tokens: Optional[float]

    class Config:
        orm_mode = True


class NetworkPerformance(BaseModel):
    max_pokt: Optional[float]
    max_relays: Optional[int]
    thirty_day_pokt_avg: Optional[float]
    thirty_day_relays_avg: Optional[int]
    today_pokt: Optional[float]
    today_relays: Optional[int]
