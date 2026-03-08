from sqlalchemy import DDL, event

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
