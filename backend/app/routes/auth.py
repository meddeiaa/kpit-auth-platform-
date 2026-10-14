"""
Routes d'authentification.

Layer 0 : register + login
Layer 1 : bcrypt + JWT + Rate Limiting + Audit Logs
Layer 2 : Intelligence Artificielle (Isolation Forest Anomaly Detection)
Layer 3 : Authentification Adaptative au Risque (Risk-Based 2FA / TOTP)
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app.extensions import db, limiter
from app.models import User
from app.models.audit import AuditLog

from app.services.anomaly_detector import anomaly_detector
from app.services.email_service import email_service


def log_audit_event(event_type, login=None, user_id=None, is_success=False):
    try:
        ip = request.remote_addr or '127.0.0.1'
        ua = request.headers.get('User-Agent', '')[:255]
        
        score, is_anomaly = anomaly_detector.evaluate_connection(
            login_attempted=login or 'unknown',
            ip_address=ip,
            is_success=is_success
        )
        
        log_entry = AuditLog(
            user_id=user_id,
            login_attempted=login,
            event=event_type,
            ip_address=ip,
            user_agent=ua,
            anomaly_score=score,
            is_anomaly=is_anomaly
        )
        db.session.add(log_entry)
        db.session.commit()
        
        return score, is_anomaly
    except Exception as e:
        db.session.rollback()
        print(f"[AUDIT/AI LOG ERROR] {e}")
        return 0.0, False


auth_ns = Namespace(
    'auth',
    description='Authentication endpoints with Risk-Based Adaptive 2FA'
)

register_model = auth_ns.model('RegisterRequest', {
    'first_name': fields.String(required=True, example='Ahmed'),
    'last_name': fields.String(required=True, example='Ben Ali'),
    'email': fields.String(required=True, example='ahmed@test.com'),
    'login': fields.String(required=True, example='ahmed'),
    'password': fields.String(required=True, example='ahmed123'),
    'role': fields.String(required=False, default='viewer', example='viewer')
})

login_model = auth_ns.model('LoginRequest', {
    'login': fields.String(required=True, example='ahmed'),
    'password': fields.String(required=True, example='ahmed123')
})

# NOUVEAU MODÈLE POUR LA VÉRIFICATION 2FA
verify_2fa_model = auth_ns.model('Verify2FARequest', {
    'login': fields.String(required=True, description='Username', example='ahmed'),
    'otp_code': fields.String(required=True, description='6-digit 2FA OTP code', example='123456')
})


@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(register_model, validate=False)
    @auth_ns.doc('register_user')
    def post(self):
        data = request.get_json() or {}

        required_fields = ['first_name', 'last_name', 'email', 'login', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return {'success': False, 'error': f'Missing or empty field: {field}'}, 400

        if len(str(data['password'])) < 6:
            return {'success': False, 'error': 'Password must be at least 6 characters'}, 400

        if User.query.filter_by(email=data['email']).first():
            return {'success': False, 'error': 'Email already registered'}, 409

        if User.query.filter_by(login=data['login']).first():
            return {'success': False, 'error': 'Login already taken'}, 409

        new_user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            login=data['login'],
            role=data.get('role', 'viewer') or 'viewer'
        )
        new_user.set_password(data['password'])
        new_user.generate_otp_secret() # Génère sa clé secrète 2FA dès l'inscription

        try:
            db.session.add(new_user)
            db.session.commit()
            
            log_audit_event('REGISTER_SUCCESS', login=new_user.login, user_id=new_user.id, is_success=True)
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Database error: {str(e)}'}, 500

        return {
            'success': True,
            'message': 'User created successfully',
            'user': new_user.to_dict()
        }, 201


@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model, validate=False)
    @auth_ns.doc('login_user')
    @limiter.limit("30 per minute")
    def post(self):
        data = request.get_json() or {}
        login_input = data.get('login')
        password_input = data.get('password')

        if not login_input or not password_input:
            score, is_anomaly = log_audit_event('LOGIN_INVALID_INPUT', login=login_input, is_success=False)
            return {'success': False, 'error': 'Login and password are required'}, 400

        user = User.query.filter_by(login=login_input).first()

        # 1. Vérification du mot de passe
        if not user or not user.check_password(password_input):
            score, is_anomaly = log_audit_event('LOGIN_FAILED', login=login_input, user_id=user.id if user else None, is_success=False)
            return {
                'success': False,
                'error': 'Invalid username or password',
                'anomaly_score': score,
                'is_anomaly': is_anomaly
            }, 401

        if not user.is_active:
            score, is_anomaly = log_audit_event('LOGIN_DISABLED_ACCOUNT', login=login_input, user_id=user.id, is_success=False)
            return {
                'success': False,
                'error': 'Account is disabled',
                'anomaly_score': score,
                'is_anomaly': is_anomaly
            }, 403

        # 2. Évaluation de la sécurité par l'IA (Layer 2)
        score, is_anomaly = log_audit_event('LOGIN_SUCCESS', login=login_input, user_id=user.id, is_success=True)

        # S'assurer que l'utilisateur possède un secret 2FA
        if not user.otp_secret:
            user.generate_otp_secret()
            db.session.commit()

        # 3. LAYER 3 : DÉCISION ADAPTATIVE AU RISQUE (Risk-Based 2FA)
        if is_anomaly or score >= 0.65:
            current_otp = user.get_totp().now()
            email_service.send_otp_email(
                recipient_email=user.email,
                otp_code=current_otp,
                user_name=user.full_name
            )
            
            return {
                'success': True,
                'require_2fa': True,
                'message': 'High risk connection detected. 2FA Verification code sent to your email.',
                'login': user.login,
                'masked_email': mask_email(user.email), # e.g. a***d@kpit.com
                'anomaly_score': score,
                'is_anomaly': True
                # 🔒 NOTE : Plus de code OTP en clair dans la réponse JSON !
            }, 200

        # Connexion Normale (Score Faible) : Délivrer le JWT immédiatement
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'login': user.login, 'role': user.role}
        )

        return {
            'success': True,
            'require_2fa': False,
            'message': f'Welcome {user.full_name}!',
            'access_token': access_token,
            'user': user.to_dict(),
            'anomaly_score': score,
            'is_anomaly': False
        }, 200


@auth_ns.route('/verify-2fa')
class Verify2FA(Resource):
    """Endpoint pour valider le code OTP à 6 chiffres lors d'une alerte IA."""

    @auth_ns.expect(verify_2fa_model)
    @auth_ns.doc('verify_2fa')
    def post(self):
        data = request.get_json() or {}
        login_input = data.get('login')
        otp_code = data.get('otp_code')

        if not login_input or not otp_code:
            return {'success': False, 'error': 'Login and OTP code are required'}, 400

        user = User.query.filter_by(login=login_input).first()

        if not user:
            return {'success': False, 'error': 'User not found'}, 404

        # Vérification du code TOTP via pyotp
        if not user.verify_otp(otp_code):
            log_audit_event('2FA_FAILED', login=login_input, user_id=user.id, is_success=False)
            return {'success': False, 'error': 'Invalid or expired 2FA code'}, 401

        # Code 2FA Valide ➔ Délivrer le Token JWT final
        log_audit_event('2FA_SUCCESS', login=login_input, user_id=user.id, is_success=True)

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'login': user.login, 'role': user.role}
        )

        return {
            'success': True,
            'message': '2FA verification successful!',
            'access_token': access_token,
            'user': user.to_dict()
        }, 200


@auth_ns.route('/me')
class Me(Resource):
    @jwt_required()
    @auth_ns.doc(security='Bearer')
    def get(self):
        user_id = get_jwt_identity()
        try:
            uid = int(user_id)
        except (TypeError, ValueError):
            return {'success': False, 'error': 'Invalid token subject'}, 401

        user = User.query.get(uid)
        if not user:
            return {'success': False, 'error': 'User not found'}, 404

        if not user.is_active:
            return {'success': False, 'error': 'Account is disabled'}, 403

        return {
            'success': True,
            'user': user.to_dict()
        }, 200



def mask_email(email: str) -> str:
    """Masque un email (ex: ahmed@kpit.com -> a***d@kpit.com)."""
    if not email or '@' not in email:
        return '***@***.com'
    parts = email.split('@')
    name = parts[0]
    domain = parts[1]
    masked_name = name[0] + '***' + name[-1] if len(name) > 2 else name[0] + '***'
    return f"{masked_name}@{domain}"    
# Modèle Swagger pour le renvoi 2FA
resend_2fa_model = auth_ns.model('Resend2FARequest', {
    'login': fields.String(required=True, description='Username', example='ahmed')
})


@auth_ns.route('/resend-2fa')
class Resend2FA(Resource):
    """Endpoint pour renvoyer un nouveau code 2FA par e-mail."""

    @auth_ns.expect(resend_2fa_model)
    @auth_ns.doc('resend_2fa')
    @limiter.limit("3 per minute")  # Max 3 renvois par minute par IP
    def post(self):
        data = request.get_json() or {}
        login_input = data.get('login')

        if not login_input:
            return {'success': False, 'error': 'Username is required'}, 400

        user = User.query.filter_by(login=login_input).first()

        if not user:
            return {'success': False, 'error': 'User not found'}, 404

        # Générer le nouveau code OTP courant
        current_otp = user.get_totp().now()

        # Renvoyer l'email Brevo
        email_service.send_otp_email(
            recipient_email=user.email,
            otp_code=current_otp,
            user_name=user.full_name
        )

        log_audit_event('2FA_RESENT', login=login_input, user_id=user.id, is_success=True)

        return {
            'success': True,
            'message': 'A new 2FA verification code has been sent to your email.'
        }, 200

    