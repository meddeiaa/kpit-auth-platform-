"""
Extensions Flask.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# ORM & Migrations
db = SQLAlchemy()
migrate = Migrate()

# JWT (Layer 1)
jwt = JWTManager()

# Rate Limiter (Layer 1)
# NOTE : default_limits est vide pour ne PAS bloquer le Polling Angular (/status)
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://"
)