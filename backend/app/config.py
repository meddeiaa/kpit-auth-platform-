"""
Configuration de l'application Flask.

Ce module définit les différentes configurations selon l'environnement :
- Development : pour développer en local
- Production : pour déployer en ligne
- Testing : pour lancer les tests
"""
import os
from datetime import timedelta


class Config:
    """Configuration de base commune à tous les environnements."""
    
    # === CLÉ SECRÈTE (utilisée pour signer les sessions Flask) ===
    # En dev, on utilise une valeur par défaut
    # En prod, on la charge depuis les variables d'environnement
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-CHANGE-IN-PRODUCTION')
    
    # === JSON (format des réponses API) ===
    # Ne pas trier les clés alphabétiquement
    JSON_SORT_KEYS = False
    
    # === API DOCUMENTATION (Swagger) ===
    RESTX_MASK_SWAGGER = False  # Désactiver le champ X-Fields
    

class DevelopmentConfig(Config):
    """Configuration pour le développement local."""
    
    DEBUG = True    # Mode debug : auto-reload + pages d'erreur détaillées
    ENV = 'development'
    

class ProductionConfig(Config):
    """Configuration pour la production."""
    
    DEBUG = False   # JAMAIS de debug en prod (dangereux !)
    ENV = 'production'


class TestingConfig(Config):
    """Configuration pour les tests automatisés."""
    
    TESTING = True
    DEBUG = True


# Dictionnaire pour choisir la config selon l'environnement
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}