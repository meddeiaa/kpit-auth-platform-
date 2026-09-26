"""
Extensions Flask.

Initialisées ici, liées à l'app dans create_app() via init_app().
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
# ORM
db = SQLAlchemy()

# Migrations
migrate = Migrate()

# JWT — Layer 1 SECURITY+
jwt = JWTManager()

# Rate Limiter (Layer 1) — Identifie les clients par leur adresse IP
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],  # Limites globales par défaut
    storage_uri="memory://"                         # Stockage en mémoire RAM
)