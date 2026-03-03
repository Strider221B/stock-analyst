from passlib.context import CryptContext
from cryptography.fernet import Fernet

from config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

ENCRYPTION_KEY = settings.db_encryption_key.encode('utf-8')

cipher_suite = Fernet(ENCRYPTION_KEY)
