"""
Service de Détection d'Anomalies de Connexion (Layer 2 - Basic AI).

Utilise Isolation Forest de scikit-learn pour évaluer le comportement
par rapport au profil habituel des connexions réussies.
"""
from datetime import datetime, timedelta
import numpy as np
from sklearn.ensemble import IsolationForest

from app.models.audit import AuditLog


class AnomalyDetectorService:
    """
    Service Machine Learning comportemental.
    """

    def __init__(self, contamination=0.1):
        self.contamination = contamination
        self.min_samples_required = 5  # 5 connexions réussies suffisent pour apprendre

    def _extract_features(self, timestamp: datetime, is_success: bool, recent_failures: int) -> list:
        """
        Feature Engineering : Vecteur [Heure, Jour, Succès, Échecs Récents].
        """
        hour_of_day = timestamp.hour + (timestamp.minute / 60.0)  # 0.0 à 23.9
        day_of_week = timestamp.weekday()                          # 0 à 6
        success_int = 1 if is_success else 0
        
        return [hour_of_day, day_of_week, success_int, recent_failures]

    def _get_recent_failures_count(self, ip_address: str, minutes=6) -> int:
        """
        Compte le nombre d'échecs de connexion récents pour cette IP.
        """
        since_time = datetime.utcnow() - timedelta(minutes=minutes)
        return AuditLog.query.filter(
            AuditLog.ip_address == ip_address,
            AuditLog.event == 'LOGIN_FAILED',
            AuditLog.timestamp >= since_time
        ).count()

    def evaluate_connection(self, login_attempted: str, ip_address: str, is_success: bool) -> tuple[float, bool]:
        """
        Évalue si la tentative courante écarte du comportement habituel.
        """
        now = datetime.utcnow()
        recent_failures = self._get_recent_failures_count(ip_address)
        
        # 1. Vecteur de la connexion actuelle
        current_features = self._extract_features(now, is_success, recent_failures)

        # 2. Récupérer l'historique des CONNEXIONS RÉUSSIES (Profil Normal)
        # On n'entraîne PAS le modèle sur les attaques pour ne pas polluer l'IA !
        success_logs = AuditLog.query.filter_by(
            event='LOGIN_SUCCESS',
            login_attempted=login_attempted 
        ).order_by(AuditLog.timestamp.desc()).limit(100).all()      # ← ISOLAT

        # Fallback Heuristique si pas assez de connexions réussies enregistrées
        if len(success_logs) < self.min_samples_required:
            if recent_failures >= 3:
                return 0.85, True  # Forte anomalie par échecs répétés
            elif not is_success:
                return 0.45, False # Échec isolé
            return 0.10, False     # Succès normal

        # 3. Matrice X_train basée EXCLUSIVEMENT sur le comportement normal habituel
        X_train = []
        for log in success_logs:
            features = self._extract_features(log.timestamp, True, 0) # Normal = 0 échec
            X_train.append(features)

        X_train = np.array(X_train)

        # 4. Entraîner Isolation Forest sur le profil normal
        model = IsolationForest(
            n_estimators=100,
            contamination=self.contamination,
            random_state=42
        )
        model.fit(X_train)

        # 5. Calculer le score pour la tentative actuelle
        raw_score = model.decision_function([current_features])[0]

        # Normaliser le score entre 0.0 et 1.0
        normalized_score = float(np.clip(0.5 - (raw_score * 2.0), 0.0, 1.0))
        
        # FACTEUR D'AMPLIFICATION SÉCURITÉ :
        # Si la tentative actuelle contient des échecs récents ou est un échec, on amplifie le score !
        if recent_failures >= 3:
            normalized_score = max(normalized_score, 0.85) # Force au moins 85% si force brute
        elif not is_success and recent_failures >= 1:
            normalized_score = max(normalized_score, 0.60) # Échecs consécutifs

        is_anomaly = normalized_score >= 0.65

        return round(normalized_score, 2), is_anomaly


# Singleton du service
anomaly_detector = AnomalyDetectorService()