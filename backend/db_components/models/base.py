from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    The master class that all SQLAlchemy models will inherit from.
    SQLAlchemy's metadata catalog is attached to this class.
    """
    pass
