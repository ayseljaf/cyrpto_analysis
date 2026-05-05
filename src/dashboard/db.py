import os

from sqlalchemy import create_engine


def get_engine():
    host = os.environ.get("CRYPTO_DB_HOST", "localhost")
    port = os.environ.get("CRYPTO_DB_PORT", "5432")
    name = os.environ.get("CRYPTO_DB_NAME", "crypto_db")
    user = os.environ.get("CRYPTO_DB_USER", "crypto_user")
    password = os.environ.get("CRYPTO_DB_PASSWORD", "")
    return create_engine(f"postgresql://{user}:{password}@{host}:{port}/{name}")
