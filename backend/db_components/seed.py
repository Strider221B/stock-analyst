# docker compose exec backend env PYTHONPATH=. python db_components/seed.py
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
                db.add(PortfolioItem(
                    user_id=user.id,
                    portfolio_id=domestic_portfolio.id,
                    ticker=ticker
                ))
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
                db.add(PortfolioItem(
                    user_id=user.id,
                    portfolio_id=international_portfolio.id,
                    ticker=ticker
                ))
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

# docker compose exec backend env PYTHONPATH=. python db_components/seed.py

# Checks
# docker exec -it stock_db_dev /bin/bash
# psql -U <db_username> -d <db_name>
# \dt

# do this only if you don't see result of below queries as we have row level policies.
# SET row_security = off;

# SELECT * FROM users;
#          email         |                                           password_hash                                           |                  id                  |          created_at           |          updated_at
# -----------------------+---------------------------------------------------------------------------------------------------+--------------------------------------+-------------------------------+-------------------------------
#  developer@example.com | $argon2id$v=19$m=65536,t=3,p=4$qOVoQ15t0YJ+oDHNSLFZdg$7o2Svd3hUPlWUU3r577B/R/NKOVNeaN0M5aEZkiNxSk | 75ee176d-cb4b-42c8-8bac-d01a622e80e3 | 2026-03-20 04:00:39.294645+00 | 2026-03-20 04:00:39.294645+00
# (1 row)

# SELECT * FROM portfolios;
#                user_id                |        name         | account_type  |                  id                  |          created_at           |          updated_at
# --------------------------------------+---------------------+---------------+--------------------------------------+-------------------------------+-------------------------------
#  75ee176d-cb4b-42c8-8bac-d01a622e80e3 | NSE Core Holdings   | DOMESTIC      | 420b0191-72ec-4d59-a7c6-410649704c7a | 2026-03-20 04:00:39.294645+00 | 2026-03-20 04:00:39.294645+00
#  75ee176d-cb4b-42c8-8bac-d01a622e80e3 | Fidelity RSU & ESPP | INTERNATIONAL | 261e0efc-c1cd-4150-b42c-e75cb9d4b6bf | 2026-03-20 04:00:39.294645+00 | 2026-03-20 04:00:39.294645+00
# (2 rows)

# SELECT * FROM portfolio_items;
#                user_id                |             portfolio_id             |   ticker    |          added_at          |                  id
# --------------------------------------+--------------------------------------+-------------+----------------------------+--------------------------------------
#  75ee176d-cb4b-42c8-8bac-d01a622e80e3 | 420b0191-72ec-4d59-a7c6-410649704c7a | RELIANCE.NS | 2026-03-20 04:00:39.294645 | 73389e3b-b275-4c9d-bf7e-2d29e36a1cac
#  75ee176d-cb4b-42c8-8bac-d01a622e80e3 | 420b0191-72ec-4d59-a7c6-410649704c7a | TCS.NS      | 2026-03-20 04:00:39.294645 | 9ccec5b9-0680-499e-9ad5-741832019ca9
#  75ee176d-cb4b-42c8-8bac-d01a622e80e3 | 420b0191-72ec-4d59-a7c6-410649704c7a | HDFCBANK.NS | 2026-03-20 04:00:39.294645 | 0dea7374-4d95-4c16-bfa0-7111a67df680
#  75ee176d-cb4b-42c8-8bac-d01a622e80e3 | 261e0efc-c1cd-4150-b42c-e75cb9d4b6bf | AAPL        | 2026-03-20 04:00:39.294645 | bf2b82ef-e631-4625-b3b1-1898a45a9389
#  75ee176d-cb4b-42c8-8bac-d01a622e80e3 | 261e0efc-c1cd-4150-b42c-e75cb9d4b6bf | GOOGL       | 2026-03-20 04:00:39.294645 | f98fe16f-a22b-4f1b-b047-60ac3d226885
#  75ee176d-cb4b-42c8-8bac-d01a622e80e3 | 261e0efc-c1cd-4150-b42c-e75cb9d4b6bf | MSFT        | 2026-03-20 04:00:39.294645 | 5f9a1781-60bd-420b-81a8-394206a5bb68
# (6 rows)

# SET row_security = on;
# ALTER ROLE <db_username> NOBYPASSRLS;

# Check if role bypass still applies, you should see an f
# SELECT rolname, rolbypassrls FROM pg_roles WHERE rolname = '<db_username>';

# Check if super user:
# SELECT rolname, rolsuper FROM pg_roles WHERE rolname = 'local_admin';
