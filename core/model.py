from typing import Optional
from pydantic import BaseModel


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


class NetworkPerformance(BaseModel):
    max_pokt: Optional[float]
    max_relays: Optional[int]
    thirty_day_pokt_avg: Optional[float]
    thirty_day_relays_avg: Optional[int]
    today_pokt: Optional[float]
    today_relays: Optional[int]
