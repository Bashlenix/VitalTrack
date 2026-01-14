import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Database configuration
    # If DB_HOST is set (e.g., in Docker Compose), construct URI from components
    # Otherwise, use SQLALCHEMY_DATABASE_URI from .env file
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME") or os.getenv("MYSQL_DATABASE")
    DB_USER = os.getenv("DB_USER") or os.getenv("MYSQL_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD") or os.getenv("MYSQL_PASSWORD")

    if DB_HOST:
        # Construct database URI for Docker Compose (using service name 'db')
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
    else:
        # Use existing SQLALCHEMY_DATABASE_URI from .env (for local development)
        SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.getenv("SECRET_KEY")
    SECURITY_PASSWORD_SALT = os.getenv("SECURITY_PASSWORD_SALT")

    # SMTP config (example: Gmail – for dev/testing use an app password)
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

    # File upload configuration
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "bmp", "tiff", "dcm", "dicom"}
    UPLOAD_FOLDER = "static/uploads/radiology"
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    # Token configuration
    MAX_AGE_SECONDS = 86400  # 24 hours

    GENDERS = ["male", "female", "other"]
