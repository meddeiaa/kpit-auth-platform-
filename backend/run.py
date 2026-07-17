"""
Point d'entrée de l'application.

Ce fichier lance le serveur Flask en mode développement.
Pour lancer : python run.py
"""
from app import create_app

# Créer l'application avec la configuration "development"
app = create_app('development')

if __name__ == '__main__':
    # Lancer le serveur de développement
    app.run(
        host='0.0.0.0',   # Écouter sur toutes les interfaces réseau
        port=5000,        # Port par défaut de Flask
        debug=True        # Auto-reload + pages d'erreur
    )