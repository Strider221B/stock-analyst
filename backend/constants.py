from enum import StrEnum

# ==========================================
# Environment & Configuration Constants
# ==========================================
class Environment(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"

class APITags(StrEnum):
    SYSTEM = "System"
    AUTH = "Authentication"
    PORTFOLIO = "Portfolios"
    ANALYSIS = "Analysis & Scanning"
    CHAT = "Real-time Chat"

# ==========================================
# Database & Domain Constants
# ==========================================
class AccountType(StrEnum):
    """Types of investment portfolios a user can create."""
    DOMESTIC = "DOMESTIC"
    INTERNATIONAL = "INTERNATIONAL"
    EMPLOYEE_EQUITY = "EMPLOYEE_EQUITY"

class AnalysisRating(StrEnum):
    """The structured output ratings from the Gemini AI."""
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"

class ChatSender(StrEnum):
    """Identifies who sent a message in the WebSocket chat."""
    USER = "USER"
    AI = "AI"

# ==========================================
# Standard String Constants (Grouped)
# ==========================================
class AppConfig:
    TITLE = "Stock Analysis AI API"
    DESCRIPTION = "Backend API."
    VERSION = "1.0.0"
    API_PREFIX = "/api"
    WS_PREFIX = "/ws"

class CORSConfig:
    """Explicitly defined CORS rules to prevent overly permissive wildcards."""

    # We allow OPTIONS because browsers use it for CORS "preflight" checks
    ALLOWED_METHODS = [
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "OPTIONS"
    ]

    # Only allow standard safe headers and the specific headers React needs
    ALLOWED_HEADERS = [
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With"
    ]

class TableNames(StrEnum):
    """Centralized table names for database models and foreign keys."""
    USERS = "users"
    PORTFOLIOS = "portfolios"
    PORTFOLIO_ITEMS = "portfolio_items"
    ANALYSIS_HISTORY = "analysis_history"
    CHAT_SESSIONS = "chat_sessions"
    CHAT_MESSAGES = "chat_messages"

class RelNames(StrEnum):
    """Centralized relationship names for SQLAlchemy back_populates."""
    USER = "user"
    PORTFOLIOS = "portfolios"
    PORTFOLIO = "portfolio"
    ITEMS = "items"
    ANALYSIS_HISTORY = "analysis_history"
    CHAT_SESSIONS = "chat_sessions"
    SESSION = "session"
    MESSAGES = "messages"
