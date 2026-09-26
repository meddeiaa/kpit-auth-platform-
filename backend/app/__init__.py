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
from app.extensions import db, migrate, jwt,limiter

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialiser les extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)
    
    # Importer les modèles pour qu'ils soient connus de SQLAlchemy
    from app.models import User, AuditLog
    
    # CRÉATION AUTOMATIQUE DES TABLES MANQUANTES DANS DEV.DB
    with app.app_context():
        db.create_all()
    
    # Configuration CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:4200"]
        }
    })
    
    # Swagger API
    authorizations = {
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': "JWT : tape 'Bearer <access_token>'"
        }
    }
    
    api = Api(
        app,
        version='1.0',
        title='KPIT Auth Platform API',
        description='AI-Enhanced Authentication Platform - REST API Documentation',
        doc='/docs',
        prefix='/api',
        authorizations=authorizations,
        security='Bearer'
    )
    
    # Namespaces
    from flask_restx import Resource, Namespace
    ns_health = Namespace('health', description='Health check endpoints')
    api.add_namespace(ns_health)
    
    @ns_health.route('')
    class HealthCheck(Resource):
        def get(self):
            return {
                'status': 'healthy',
                'message': 'KPIT Auth Platform API is running',
                'version': '1.0.0'
            }
    
    from app.routes.auth import auth_ns
    api.add_namespace(auth_ns)
    
    from app.routes.test_manager import test_ns
    api.add_namespace(test_ns)
    
    return app
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
    jwt.init_app(app)
    limiter.init_app(app)
    
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
    # SWAGGER API CONFIGURATION
    # ============================================
    
    # 1. Définition du schéma de sécurité Swagger (OpenAPI)
    authorizations = {
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': "Tapez 'Bearer ' suivi de votre token. Exemple: Bearer eyJhbGciOi..."
        }
    }
    
    # 2. Création de l'instance API avec la sécurité activée
    api = Api(
        app,
        version='1.0',
        title='KPIT Auth Platform API',
        description='AI-Enhanced Authentication Platform - REST API Documentation',
        doc='/docs',
        prefix='/api',
        authorizations=authorizations,  # ← AJOUT ICI
        security='Bearer'               # ← AJOUT ICI (Active le cadenas globalement)
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
    # --- Namespace : Tests Manager ---
    from app.routes.test_manager import test_ns
    api.add_namespace(test_ns)
    
    return app