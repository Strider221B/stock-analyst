from sqlalchemy.types import TypeDecorator, LargeBinary
from db_components.security import cipher_suite

class EncryptedText(TypeDecorator):
    """Transparently encrypts and decrypts text data at rest."""
    impl = LargeBinary
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            # Encrypt the string and return raw bytes to the DB
            return cipher_suite.encrypt(value.encode('utf-8'))
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            # Decrypt the bytes and return a UTF-8 string to the application
            return cipher_suite.decrypt(value).decode('utf-8')
        return value
