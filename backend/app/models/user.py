"""
Modèle User - Représente un utilisateur dans la base de données.

Layer 1 — SECURITY+ :
Les mots de passe sont hashés avec bcrypt (salt + cost factor).
"""
from datetime import datetime
import bcrypt

from app.extensions import db


class User(db.Model):
    """
    Modèle User - Un utilisateur de l'application.

    Attributes:
        id, first_name, last_name, email, login,
        password (HASH bcrypt, jamais le clair),
        role, is_active, created_at, updated_at
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)

    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    login = db.Column(db.String(50), unique=True, nullable=False, index=True)

    # Stocke le HASH bcrypt (ex: $2b$12$...), pas le mot de passe clair
    password = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), default='viewer', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return f'<User {self.login} ({self.email})>'

    # ============================================
    # LAYER 1 — BCRYPT
    # ============================================

    def set_password(self, plain_password: str) -> None:
        """
        Hash le mot de passe clair et le stocke dans self.password.

        - gensalt() : salt aléatoire unique (protège contre rainbow tables)
        - rounds=12 : cost factor (compromis sécu / perf ~100ms)
        - decode : on stocke une str UTF-8 en DB, pas des bytes bruts
        """
        if not plain_password:
            raise ValueError('Password cannot be empty')

        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
        self.password = hashed.decode('utf-8')

    def check_password(self, plain_password: str) -> bool:
        """
        Vérifie un mot de passe clair contre la valeur en base.

        Cas 1 — Hash bcrypt (Layer 1) :
            bcrypt.checkpw(clair, hash)

        Cas 2 — Ancien clair Layer 0 (migration douce) :
            si égalité, on re-hash immédiatement (upgrade)
            puis on retourne True

        Returns:
            True si le mot de passe est correct, False sinon.
        """
        if not plain_password or not self.password:
            return False

        stored = self.password

        # --- Cas bcrypt moderne ---
        if self._is_bcrypt_hash(stored):
            try:
                return bcrypt.checkpw(
                    plain_password.encode('utf-8'),
                    stored.encode('utf-8')
                )
            except (ValueError, TypeError):
                return False

        # --- Cas legacy Layer 0 (texte clair) ---
        if stored == plain_password:
            # Upgrade transparent : prochain login utilisera uniquement bcrypt
            self.set_password(plain_password)
            try:
                db.session.add(self)
                db.session.commit()
            except Exception:
                db.session.rollback()
                # Même si le commit échoue, l'auth de CE request reste valide
            return True

        return False

    @staticmethod
    def _is_bcrypt_hash(value: str) -> bool:
        """Détecte un hash bcrypt ($2a$, $2b$, $2y$)."""
        if not value or not isinstance(value, str):
            return False
        return value.startswith(('$2a$', '$2b$', '$2y$')) and len(value) >= 50

    def to_dict(self, include_password=False):
        """
        Sérialisation JSON.
        Par défaut : JAMAIS le hash (ni le clair).
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

        if include_password:
            # Uniquement pour debug local — JAMAIS en production / dans les routes
            data['password'] = self.password

        return data

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'