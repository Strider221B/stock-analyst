from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Annotated

from apis.portfolio_schemas import PortfolioCreate, PortfolioItemCreate, PortfolioResponse
from apis.schemas import MessageResponse
from db_components.database import get_db
from db_components.models.portfolio import Portfolio
from db_components.models.portfolio_item import PortfolioItem
from fastapi import APIRouter, Depends, HTTPException, status
from routers.dependencies import get_current_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, Session
from db_components.models.user import User

router = APIRouter(
    prefix="/api/portfolios",
    tags=["Portfolios"],
)

@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_portfolio(
    portfolio_data: PortfolioCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    new_portfolio = Portfolio(
        user_id=current_user.id,
        name=portfolio_data.name,
        account_type=portfolio_data.account_type,
    )
    db.add(new_portfolio)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        if e.orig and getattr(e.orig, "pgcode", None) == "23505":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Portfolio already exists",
            ) from e
        raise
    return MessageResponse(message="Portfolio created successfully")

@router.get("", response_model=list[PortfolioResponse])
def get_portfolios(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Portfolio]:
    portfolios = (
        db.query(Portfolio)
        .options(joinedload(Portfolio.items))
        .filter(Portfolio.user_id == current_user.id)
        .all()
    )
    return portfolios

@router.post("/{portfolio_id}/items", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def add_portfolio_item(
    portfolio_id: uuid.UUID,
    item_data: PortfolioItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found",
        )

    new_item = PortfolioItem(
        user_id=current_user.id,
        portfolio_id=portfolio.id,
        ticker=item_data.ticker.upper(),
    )
    db.add(new_item)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        if e.orig and getattr(e.orig, "pgcode", None) == "23505":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ticker already exists in portfolio",
            ) from e
        raise

    return MessageResponse(message="Ticker added successfully")

@router.delete("/{portfolio_id}/items/{ticker}", response_model=MessageResponse)
def remove_portfolio_item(
    portfolio_id: uuid.UUID,
    ticker: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MessageResponse:
    item = db.query(PortfolioItem).filter(
        PortfolioItem.portfolio_id == portfolio_id,
        PortfolioItem.ticker == ticker.upper(),
        PortfolioItem.user_id == current_user.id
    ).first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticker not found in portfolio",
        )

    db.delete(item)
    db.commit()

    return MessageResponse(message="Ticker removed successfully")
