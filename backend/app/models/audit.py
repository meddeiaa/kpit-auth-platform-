"""
Modèle AuditLog - Enregistre les événements de sécurité (Layer 1 SECURITY+).
"""
from datetime import datetime
from app.extensions import db


class AuditLog(db.Model):
    """
    Table 'audit_logs' pour la traçabilité des connexions et actions de sécurité.
    """
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=True)          # ID de l'utilisateur (si connu)
    login_attempted = db.Column(db.String(50), nullable=True) # Login saisi lors de la tentative
    event = db.Column(db.String(50), nullable=False)        # ex: LOGIN_SUCCESS, LOGIN_FAILED, REGISTER
    ip_address = db.Column(db.String(45), nullable=True)   # Adresse IP (IPv4 ou IPv6)
    user_agent = db.Column(db.String(255), nullable=True)   # Navigateur / Client
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'login_attempted': self.login_attempted,
            'event': self.event,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat()
        }