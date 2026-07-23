"""
Configuration de l'application Flask.

Ce module définit les différentes configurations selon l'environnement :
- Development : pour développer en local (SQLite)
- Production : pour déployer en ligne (MySQL/PostgreSQL)
- Testing : pour lancer les tests (SQLite en mémoire)
"""
import os
from datetime import timedelta


class Config:
    """Configuration de base commune à tous les environnements."""
    
    # ============================================
    # SÉCURITÉ
    # ============================================
    
    # Clé secrète (utilisée pour signer les cookies)
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-CHANGE-IN-PRODUCTION')
    
    # ============================================
    # JSON
    # ============================================
    
    # Ne pas trier les clés alphabétiquement dans les réponses JSON
    JSON_SORT_KEYS = False
    
    # ============================================
    # API DOCUMENTATION (Swagger)
    # ============================================
    
    RESTX_MASK_SWAGGER = False
    
    # ============================================
    # BASE DE DONNÉES (SQLAlchemy)
    # ============================================
    
    # Désactive une fonctionnalité obsolète qui consomme de la mémoire
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """Configuration pour le développement local."""
    
    DEBUG = True
    ENV = 'development'
    
    # === BASE DE DONNÉES : SQLite ===
    # Format : sqlite:///nom_du_fichier.db
    # Le fichier dev.db sera créé dans le dossier backend/
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'


class ProductionConfig(Config):
    """Configuration pour la production."""
    
    DEBUG = False
    ENV = 'production'
    
    # === BASE DE DONNÉES : MySQL (via variable d'environnement) ===
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://user:pass@localhost/kpit_auth'
    )


class TestingConfig(Config):
    """Configuration pour les tests automatisés."""
    
    TESTING = True
    DEBUG = True
    
    # === BASE DE DONNÉES : SQLite en mémoire ===
    # ':memory:' = pas de fichier, la BD existe uniquement pendant les tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# ============================================
# DICTIONNAIRE DES CONFIGURATIONS
# ============================================
# Permet de choisir la config selon l'environnement
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}