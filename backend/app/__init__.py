"""
Application Factory Flask.

Ce module contient la fonction create_app() qui crée et configure
l'application Flask avec toutes ses extensions.
"""
from flask import Flask
from flask_cors import CORS
from flask_restx import Api

from app.config import config
from app.extensions import db, migrate


def create_app(config_name='development'):
    """
    Créer et configurer une instance de l'application Flask.
    
    Args:
        config_name (str): Nom de la configuration à utiliser
    
    Returns:
        Flask: Instance de l'application Flask configurée
    """
    # ============================================
    # CRÉER L'INSTANCE FLASK
    # ============================================
    app = Flask(__name__)
    
    # ============================================
    # CHARGER LA CONFIGURATION
    # ============================================
    app.config.from_object(config[config_name])
    
    # ============================================
    # INITIALISER LES EXTENSIONS
    # ============================================
    db.init_app(app)
    migrate.init_app(app, db)
    
    # ============================================
    # IMPORTER LES MODÈLES
    # ============================================
    from app.models import User
    
    # ============================================
    # CORS
    # ============================================
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:4200"]
        }
    })
    
    # ============================================
    # SWAGGER API
    # ============================================
    api = Api(
        app,
        version='1.0',
        title='KPIT Auth Platform API',
        description='AI-Enhanced Authentication Platform - REST API Documentation',
        doc='/docs',
        prefix='/api'
    )
    
    # ============================================
    # NAMESPACES (Blueprints)
    # ============================================
    from flask_restx import Resource, Namespace
    
    # --- Namespace : Health ---
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
    
    # --- Namespace : Auth ---
    from app.routes.auth import auth_ns
    api.add_namespace(auth_ns)
    
    return app