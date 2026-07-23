"""
Extensions Flask.

Ce module initialise toutes les extensions Flask sans les lier
à une application spécifique. Elles seront liées dans __init__.py
via la méthode init_app().

Ce pattern permet d'éviter les imports circulaires et de tester
plus facilement l'application.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# ============================================
# EXTENSIONS FLASK
# ============================================

# ORM - Object Relational Mapper
# Permet de manipuler la base de données avec des objets Python
# au lieu d'écrire du SQL brut
db = SQLAlchemy()

# Migrations de base de données
# Permet de faire évoluer le schéma de la BD sans perdre les données
# (comme un système de versioning pour la BD)
migrate = Migrate()