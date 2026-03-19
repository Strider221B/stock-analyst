# /backend/db_components/rls_utils.py
from contextvars import ContextVar
from sqlalchemy import DDL, event
from sqlalchemy.engine import Engine

# ---------------------------------------------------------
# 1. THE KEY: Context Variable for FastAPI Requests
# ---------------------------------------------------------
# This holds the user's ID securely in memory while an async request is processing.
current_user_id_ctx_var: ContextVar[str | None] = ContextVar("current_user_id", default=None)

# ---------------------------------------------------------
# 2. THE LOCKS: DDL Generators (Your existing code)
# ---------------------------------------------------------
def get_rls_statements(table_name: str, owner_column: str = "user_id"):
    """
    Generates the standard 3-step RLS setup:
    1. Enable RLS
    2. Force RLS (applies to table owner/service account)
    3. Create the isolation policy based on a session variable
    """
    policy_name = f"{table_name}_isolation_policy"

    return [
        f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;",
        f"ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY;",
        f"DROP POLICY IF EXISTS {policy_name} ON {table_name};",
        f"CREATE POLICY {policy_name} ON {table_name} "
        f"USING ({owner_column} = current_setting('app.current_user_id', true)::uuid);"
    ]

def attach_rls_to_model(model_class, owner_column: str = "user_id"):
    """
    Attaches RLS DDL to the SQLAlchemy 'after_create' event.
    Use this inside your Model files.
    """
    statements = get_rls_statements(model_class.__tablename__, owner_column)
    for stmt in statements:
        event.listen(model_class.__table__, "after_create", DDL(stmt))

# ---------------------------------------------------------
# 3. THE BRIDGE: Session Checkout Listener
# ---------------------------------------------------------
# *(Note: Ensure that whatever file creates your SQLAlchemy `engine` imports this `rls_utils` file so the event listener is actively registered!)*
@event.listens_for(Engine, "checkout")
def set_tenant_context(dbapi_connection, connection_record, connection_proxy):
    """
    Intercepts every connection right before SQLAlchemy uses it.
    Reads the ContextVar and injects the user ID directly into the Postgres session.
    """
    user_id = current_user_id_ctx_var.get()
    cursor = dbapi_connection.cursor()

    try:
        if user_id:
            # SET LOCAL scopes the variable strictly to the current database transaction.
            # Use Postgres's built-in function to set variables safely
            cursor.execute("SELECT set_config('app.current_user_id', %s, true);", (str(user_id),))

        else:
            # If no user is logged in, explicitly clear the setting so Postgres defaults to denying access.
            cursor.execute("SELECT set_config('app.current_user_id', '', true);")
    finally:
        cursor.close()
