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
