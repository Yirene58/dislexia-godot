import os
from datetime import timedelta


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://rpg_user:rpg_password@localhost:5432/dislexia_db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
