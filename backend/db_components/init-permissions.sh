#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL

    -- 1. Create the new restricted user
    CREATE USER $API_USER WITH ENCRYPTED PASSWORD '$API_USER_PASSWORD';

    -- 2. Grant basic connection rights to the database
    GRANT CONNECT ON DATABASE equity_analysis_db TO $API_USER;

    -- 3. Grant usage on the public schema (where your tables live)
    GRANT USAGE ON SCHEMA public TO $API_USER;

    -- 4. Grant specific CRUD privileges on all EXISTING tables
    -- (This includes users, portfolios, portfolio_items, etc.)
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO $API_USER;

    -- 5. Grant permissions on sequences (Required if you ever use SERIAL/auto-incrementing IDs)
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO $API_USER;

    -- 6. FUTURE-PROOFING: Ensure the $API_USER gets these exact same rights
    -- automatically whenever you create a new table in the future via Alembic.
    ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO $API_USER;

    ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO $API_USER;

    -- 7. FUTURE-PROOFING: Default Privileges for the ADMIN role (Alembic)
    -- It tells Postgres: "Whenever 'local_admin'
    -- creates a table, automatically grant these rights to '$API_USER'."
    ALTER DEFAULT PRIVILEGES FOR ROLE local_admin IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO $API_USER;

    ALTER DEFAULT PRIVILEGES FOR ROLE local_admin IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO $API_USER;
