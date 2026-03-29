from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from constants import AccountType

class PortfolioItemCreate(BaseModel):
    ticker: str = Field(..., max_length=20, min_length=1)

class PortfolioItemResponse(BaseModel):
    id: uuid.UUID
    ticker: str
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PortfolioCreate(BaseModel):
    name: str = Field(..., max_length=100)
    account_type: AccountType

class PortfolioResponse(BaseModel):
    id: uuid.UUID
    name: str
    account_type: AccountType
    items: list[PortfolioItemResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
