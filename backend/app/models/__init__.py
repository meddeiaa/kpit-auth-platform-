"""
Package models - Contient tous les modèles de base de données.

Ce fichier importe tous les modèles pour qu'ils soient facilement
accessibles depuis d'autres modules.
"""
from app.models.user import User

# Liste de tous les modèles exportés
__all__ = ['User']