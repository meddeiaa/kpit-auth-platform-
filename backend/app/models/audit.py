"""
Modèle AuditLog - Enregistre les événements de sécurité et le score d'anomalie IA (Layer 2).
"""
from datetime import datetime
from app.extensions import db


class AuditLog(db.Model):
    """
    Table 'audit_logs' pour la traçabilité et l'analyse comportementale par Machine Learning.
    """
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=True)             # ID de l'utilisateur (si connu)
    login_attempted = db.Column(db.String(50), nullable=True)    # Login saisi
    event = db.Column(db.String(50), nullable=False)           # ex: LOGIN_SUCCESS, LOGIN_FAILED
    ip_address = db.Column(db.String(45), nullable=True)      # Adresse IP
    user_agent = db.Column(db.String(255), nullable=True)      # Client HTTP
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # --- LAYER 2 : MACHINE LEARNING ---
    anomaly_score = db.Column(db.Float, default=0.0, nullable=False) # Score de 0.0 (Normal) à 1.0 (Anomalie)
    is_anomaly = db.Column(db.Boolean, default=False, nullable=False) # True si score >= 0.65

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'login_attempted': self.login_attempted,
            'event': self.event,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat(),
            'anomaly_score': round(self.anomaly_score, 2),
            'is_anomaly': self.is_anomaly
        }