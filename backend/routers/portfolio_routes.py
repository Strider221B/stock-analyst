from __future__ import annotations

import uuid
from typing import Annotated

from apis.portfolio_schemas import PortfolioCreate, PortfolioItemCreate, PortfolioResponse
from apis.schemas import MessageResponse
from constants import APITags
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
    tags=[APITags.PORTFOLIO],
)

@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    portfolio_data: PortfolioCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
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
        # psycopg2 uses pgcode, psycopg3 uses sqlstate
        if e.orig and getattr(e.orig, "pgcode", getattr(e.orig, "sqlstate", None)) == "23505":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Portfolio already exists",
            ) from e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during portfolio creation",
        ) from e
    return MessageResponse(message="Portfolio created successfully")

@router.get("", response_model=list[PortfolioResponse])
async def get_portfolios(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
) -> list[Portfolio]:
    portfolios = (
        db.query(Portfolio)
        .options(joinedload(Portfolio.items))
        .filter(Portfolio.user_id == current_user.id)
        .order_by(Portfolio.created_at.desc())
        .all()
    )
    return portfolios

@router.post(
    "/{portfolio_id}/items",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_portfolio_item(
    portfolio_id: uuid.UUID,
    item_data: PortfolioItemCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
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
        # psycopg2 uses pgcode, psycopg3 uses sqlstate
        if e.orig and getattr(e.orig, "pgcode", getattr(e.orig, "sqlstate", None)) == "23505":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ticker already exists in portfolio",
            ) from e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error adding portfolio item",
        ) from e

    return MessageResponse(message="Ticker added successfully")

@router.delete("/{portfolio_id}/items/{ticker}", response_model=MessageResponse)
async def remove_portfolio_item(
    portfolio_id: uuid.UUID,
    ticker: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
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
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error removing portfolio item",
        ) from e

    return MessageResponse(message="Ticker removed successfully")
