from typing import Optional
from sqlalchemy import Index, Column, DECIMAL, String, BigInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel

Base = declarative_base()


class RunnerPerformanceOrm(Base):
    __tablename__ = 'runner_performance'
    id = Column(BigInteger, primary_key=True)
    runner_domain = Column(String, unique=False, nullable=False)
    relays_last_48_hours = Column(BigInteger, nullable=False)
    relays_last_24_hours = Column(BigInteger, nullable=False)
    relays_last_6_hours = Column(BigInteger, nullable=False)
    serviced_last_48_hours = Column(DECIMAL, nullable=False)
    serviced_last_24_hours = Column(DECIMAL, nullable=False)
    serviced_last_6_hours = Column(DECIMAL, nullable=False)
    producer_rewards_last_48_hours = Column(DECIMAL, nullable=False)
    producer_rewards_last_24_hours = Column(DECIMAL, nullable=False)
    producer_rewards_last_6_hours = Column(DECIMAL, nullable=False)
    total_last_48_hours = Column(DECIMAL, nullable=False)
    total_last_24_hours = Column(DECIMAL, nullable=False)
    total_last_6_hours = Column(DECIMAL, nullable=False)
    avg_relays_last_48_hours = Column(DECIMAL, nullable=False)
    avg_relays_last_24_hours = Column(DECIMAL, nullable=False)
    avg_relays_last_6_hours = Column(DECIMAL, nullable=False)
    avg_last_48_hours = Column(DECIMAL, nullable=False)
    avg_last_24_hours = Column(DECIMAL, nullable=False)
    avg_last_6_hours = Column(DECIMAL, nullable=False)
    avg_base_last_48_hours = Column(DECIMAL, nullable=False)
    avg_base_last_24_hours = Column(DECIMAL, nullable=False)
    avg_base_last_6_hours = Column(DECIMAL, nullable=False)
    avg_total_last_48_hours = Column(DECIMAL, nullable=False)
    avg_total_last_24_hours = Column(DECIMAL, nullable=False)
    avg_total_last_6_hours = Column(DECIMAL, nullable=False)
    avg_producer_last_48_hours = Column(DECIMAL, nullable=False)
    avg_producer_last_24_hours = Column(DECIMAL, nullable=False)
    avg_producer_last_6_hours = Column(DECIMAL, nullable=False)
    producer_times_last_48_hours = Column(DECIMAL, nullable=False)
    producer_times_last_24_hours = Column(DECIMAL, nullable=False)
    producer_times_last_6_hours = Column(DECIMAL, nullable=False)
    total_tokens_staked = Column(BigInteger, nullable=False)
    total_validator_tokens_staked = Column(BigInteger, nullable=False)
    validators = Column(BigInteger, nullable=False)
    last_height = Column(BigInteger, nullable=False)
    total_pending_relays = Column(BigInteger, nullable=False)
    total_estimated_pending_rewards = Column(DECIMAL, nullable=False)
    total_chains = Column(BigInteger, nullable=False)
    jailed_now = Column(BigInteger, nullable=False)
    total_balance = Column(DECIMAL, nullable=False)
    total_output_balance = Column(DECIMAL, nullable=False)
    total_nodes = Column(BigInteger, nullable=False)
    nodes_staked = Column(BigInteger, nullable=False)
    nodes_unstaked = Column(BigInteger, nullable=False)
    nodes_unstaking = Column(BigInteger, nullable=False)
    tokens = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, nullable=False)


Index('runner_performance_created_at_idx', RunnerPerformanceOrm.created_at)


class RunnerPerformance(BaseModel):
    runner_domain: str
    relays_last_48_hours: Optional[int]
    relays_last_24_hours: Optional[int]
    relays_last_6_hours: Optional[int]
    serviced_last_48_hours: Optional[float]
    serviced_last_24_hours: Optional[float]
    serviced_last_6_hours: Optional[float]
    producer_rewards_last_48_hours: Optional[float]
    producer_rewards_last_24_hours: Optional[float]
    producer_rewards_last_6_hours: Optional[float]
    total_last_48_hours: Optional[float]
    total_last_24_hours: Optional[float]
    total_last_6_hours: Optional[float]
    avg_relays_last_48_hours: Optional[float]
    avg_relays_last_24_hours: Optional[float]
    avg_relays_last_6_hours: Optional[float]
    avg_last_48_hours: Optional[float]
    avg_last_24_hours: Optional[float]
    avg_last_6_hours: Optional[float]
    avg_base_last_48_hours: Optional[float]
    avg_base_last_24_hours: Optional[float]
    avg_base_last_6_hours: Optional[float]
    avg_total_last_48_hours: Optional[float]
    avg_total_last_24_hours: Optional[float]
    avg_total_last_6_hours: Optional[float]
    avg_producer_last_48_hours: Optional[float]
    avg_producer_last_24_hours: Optional[float]
    avg_producer_last_6_hours: Optional[float]
    producer_times_last_48_hours: Optional[float]
    producer_times_last_24_hours: Optional[float]
    producer_times_last_6_hours: Optional[float]
    total_tokens_staked: Optional[int]
    total_validator_tokens_staked: Optional[int]
    validators: Optional[int]
    last_height: Optional[int]
    total_pending_relays: Optional[int]
    total_estimated_pending_rewards: Optional[float]
    total_chains: Optional[int]
    jailed_now: Optional[int]
    total_balance: Optional[float]
    total_output_balance: Optional[float]
    total_nodes: Optional[int]
    nodes_staked: Optional[int]
    nodes_unstaked: Optional[int]
    nodes_unstaking: Optional[int]
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
