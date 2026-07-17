"""
Application Factory Flask.

Ce module contient la fonction create_app() qui crée et configure
l'application Flask. C'est le pattern "Application Factory" recommandé
par la documentation officielle de Flask.

Avantages :
- Facilite les tests (on peut créer plusieurs instances)
- Évite les imports circulaires
- Configuration flexible selon l'environnement
"""
from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from app.config import config


def create_app(config_name='development'):
    """
    Créer et configurer une instance de l'application Flask.
    x
    Args:
        config_name (str): Nom de la configuration à utiliser
                          ('development', 'production', 'testing')
    
    Returns:
        Flask: Instance de l'application Flask configurée
    """
    # === CRÉER L'INSTANCE FLASK ===
    app = Flask(__name__)
    
    # === CHARGER LA CONFIGURATION ===
    app.config.from_object(config[config_name])
    
    # === ACTIVER CORS ===
    # Permet à Angular (sur un autre port) de parler à Flask
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:4200"]  # Port Angular par défaut
        }
    })
    
    # === CONFIGURER SWAGGER (Documentation Auto) ===
    api = Api(
        app,
        version='1.0',
        title='KPIT Auth Platform API',
        description='AI-Enhanced Authentication Platform - REST API Documentation',
        doc='/docs',        # URL de Swagger : http://localhost:5000/docs
        prefix='/api'       # Toutes les routes commencent par /api
    )
    
    # === ROUTE DE TEST (Hello World) ===
    from flask_restx import Resource, Namespace
    
    # Créer un "namespace" (groupe de routes)
    ns_health = Namespace('health', description='Health check endpoints')
    api.add_namespace(ns_health)
    
    @ns_health.route('')
    class HealthCheck(Resource):
        """Vérifier que l'API est en ligne."""
        
        def get(self):
            """Retourne le statut de l'API."""
            return {
                'status': 'healthy',
                'message': 'KPIT Auth Platform API is running',
                'version': '1.0.0'
            }
    
    # === RETOURNER L'APP CONFIGURÉE ===
    return app