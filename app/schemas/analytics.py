from pydantic import BaseModel


class RiskSnapshotRead(BaseModel):
    id: int
    position_id: str
    health_factor: float
    eligible: bool

    class Config:
        from_attributes = True
