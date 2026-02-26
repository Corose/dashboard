import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey")

    database_url = os.environ.get("DATABASE_URL")

    # Si estamos en Render (PostgreSQL)
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace(
                "postgres://",
                "postgresql://",
                1
            )
        SQLALCHEMY_DATABASE_URI = database_url

    # Si estamos en local → usar SQLite
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False