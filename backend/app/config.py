"""
Configuration Flask selon l'environnement.
"""
import os
from datetime import timedelta


class Config:
    """Configuration commune."""

    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-CHANGE-IN-PRODUCTION')

    # --- JWT (Layer 1) ---
    # En prod : définir JWT_SECRET_KEY dans l'environnement (longue et aléatoire)
    JWT_SECRET_KEY = os.getenv(
        'JWT_SECRET_KEY',
        os.getenv('SECRET_KEY', 'dev-jwt-secret-CHANGE-IN-PRODUCTION')
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    # Plus tard : JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

    JSON_SORT_KEYS = False
    RESTX_MASK_SWAGGER = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'


class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://user:pass@localhost/kpit_auth'
    )


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}