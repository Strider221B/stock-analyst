# /backend/seed.py
import logging
from sqlalchemy.exc import IntegrityError
from db_components.database import SessionLocal
from db_components.models import User, Portfolio, PortfolioItem
from constants import AccountType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def seed_database():
    db = SessionLocal()
    try:
        logger.info("Starting database seed process...")

        # 1. Create a Test User
        test_email = "developer@example.com"
        user = db.query(User).filter(User.email == test_email).first()

        if not user:
            # Change 4: Passing 'password' as a kwarg here automatically triggers
            # the @password.setter logic defined in the User model, hashing it instantly.
            user = User(email=test_email, password="SecurePassword123!")
            db.add(user)

            # Change 2: Flush to get the user.id without committing the transaction
            db.flush()
            logger.info(f"Created test user: {test_email}")
        else:
            logger.info(f"Test user already exists: {test_email}")

        # 2. Create a DOMESTIC Portfolio
        domestic_portfolio = db.query(Portfolio).filter(
            Portfolio.user_id == user.id,
            Portfolio.name == "NSE Core Holdings"
        ).first()

        if not domestic_portfolio:
            domestic_portfolio = Portfolio(
                user_id=user.id,
                name="NSE Core Holdings",
                account_type=AccountType.DOMESTIC,
                description="Primary domestic equity tracking"
            )
            db.add(domestic_portfolio)
            db.flush() # Flush to get the domestic_portfolio.id
            logger.info("Created DOMESTIC portfolio.")

        # Change 3: Check existence of PortfolioItems inside the loop
        domestic_tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
        for ticker in domestic_tickers:
            existing_item = db.query(PortfolioItem).filter(
                PortfolioItem.portfolio_id == domestic_portfolio.id,
                PortfolioItem.ticker == ticker
            ).first()
            if not existing_item:
                db.add(PortfolioItem(portfolio_id=domestic_portfolio.id, ticker=ticker))
                logger.info(f"Added ticker {ticker} to DOMESTIC portfolio.")

        # 3. Create an INTERNATIONAL Portfolio
        international_portfolio = db.query(Portfolio).filter(
            Portfolio.user_id == user.id,
            Portfolio.name == "Fidelity RSU & ESPP"
        ).first()

        if not international_portfolio:
            international_portfolio = Portfolio(
                user_id=user.id,
                name="Fidelity RSU & ESPP",
                account_type=AccountType.INTERNATIONAL,
                description="Vested employer stock and international assets"
            )
            db.add(international_portfolio)
            db.flush() # Flush to get the international_portfolio.id
            logger.info("Created INTERNATIONAL portfolio.")

        # Change 3: Check existence of PortfolioItems inside the loop
        international_tickers = ["AAPL", "GOOGL", "MSFT"]
        for ticker in international_tickers:
            existing_item = db.query(PortfolioItem).filter(
                PortfolioItem.portfolio_id == international_portfolio.id,
                PortfolioItem.ticker == ticker
            ).first()
            if not existing_item:
                db.add(PortfolioItem(portfolio_id=international_portfolio.id, ticker=ticker))
                logger.info(f"Added ticker {ticker} to INTERNATIONAL portfolio.")

        # Change 1: A single, atomic commit at the very end.
        db.commit()
        logger.info("Database seeding completed successfully!")

    except IntegrityError as e:
        db.rollback()
        logger.error(f"Database integrity error during seeding: {e}")
    except Exception as e:
        db.rollback()
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
