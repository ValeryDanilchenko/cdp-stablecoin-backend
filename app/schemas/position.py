from pydantic import BaseModel


class PositionCreate(BaseModel):
    position_id: str
    owner_address: str
    collateral_symbol: str
    collateral_amount: str
    debt_symbol: str
    debt_amount: str


class PositionRead(BaseModel):
    id: int
    position_id: str
    owner_address: str
    collateral_symbol: str
    collateral_amount: str
    debt_symbol: str
    debt_amount: str

    class Config:
        from_attributes = True
