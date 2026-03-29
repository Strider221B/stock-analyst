from pydantic import BaseModel

class PricePoint(BaseModel):
    date: str
    price: float
