from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = "d1745d17d8a0068adb0c255fe9fdd331"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR / 'app.db'}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
