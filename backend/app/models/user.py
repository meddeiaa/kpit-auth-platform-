"""
Modèle User - Représente un utilisateur dans la base de données.

Ce modèle définit la structure de la table 'users' avec toutes
les colonnes nécessaires pour l'authentification et la gestion
des utilisateurs.
"""
from datetime import datetime
from app.extensions import db


class User(db.Model):
    """
    Modèle User - Un utilisateur de l'application.
    
    Cette classe représente la table 'users' dans la base de données.
    Chaque instance de cette classe correspond à une ligne dans la table.
    
    Attributes:
        id (int): Identifiant unique auto-généré
        first_name (str): Prénom de l'utilisateur
        last_name (str): Nom de famille
        email (str): Email unique (utilisé pour la connexion)
        login (str): Login unique (nom d'utilisateur)
        password (str): Mot de passe (sera haché avec bcrypt plus tard)
        role (str): Rôle de l'utilisateur (admin, tester, viewer)
        is_active (bool): Compte actif ou désactivé
        created_at (datetime): Date de création du compte
        updated_at (datetime): Date de dernière modification
    """
    
    # ============================================
    # NOM DE LA TABLE
    # ============================================
    __tablename__ = 'users'
    
    # ============================================
    # COLONNES
    # ============================================
    
    # ID unique auto-généré (clé primaire)
    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )
    
    # Informations personnelles
    first_name = db.Column(
        db.String(50),
        nullable=False  # Ce champ est OBLIGATOIRE
    )
    
    last_name = db.Column(
        db.String(50),
        nullable=False
    )
    
    # Email (unique = deux utilisateurs ne peuvent pas avoir le même email)
    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False,
        index=True  # Index pour recherche rapide
    )
    
    # Login / Username
    login = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Mot de passe (sera haché avec bcrypt dans une prochaine étape)
    password = db.Column(
        db.String(255),  # 255 caractères car le hash bcrypt fait ~60 caractères
        nullable=False
    )
    
    # Rôle de l'utilisateur (pour RBAC : Role-Based Access Control)
    role = db.Column(
        db.String(20),
        default='viewer',  # Valeur par défaut si non spécifiée
        nullable=False
    )
    
    # Statut du compte (actif ou désactivé)
    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )
    
    # ============================================
    # TIMESTAMPS
    # ============================================
    
    # Date de création (remplie automatiquement à la création)
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    # Date de dernière modification (mise à jour auto)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,  # Se met à jour à chaque modification
        nullable=False
    )
    
    # ============================================
    # MÉTHODES
    # ============================================
    
    def __repr__(self):
        """
        Représentation string pour le debug.
        
        Quand tu print un objet User, ça affichera :
        <User ahmed (ahmed@test.com)>
        """
        return f'<User {self.login} ({self.email})>'
    
    def to_dict(self, include_password=False):
        """
        Convertit l'objet User en dictionnaire (pour les réponses JSON).
        
        Args:
            include_password (bool): Inclure le mot de passe ? 
                                    (JAMAIS TRUE en production !)
        
        Returns:
            dict: Représentation de l'utilisateur en dictionnaire
        """
        data = {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'login': self.login,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # ⚠️ ATTENTION : NE JAMAIS inclure le mot de passe dans les réponses API !
        if include_password:
            data['password'] = self.password
        
        return data
    
    @property
    def full_name(self):
        """
        Retourne le nom complet.
        
        Exemple : "Ahmed Ben Ali"
        
        C'est une @property : on peut l'utiliser comme un attribut
        (user.full_name) sans les parenthèses (user.full_name()).
        """
        return f'{self.first_name} {self.last_name}'