"""
Routes d'authentification.

Layer 0 : register + login
Layer 1 : bcrypt + JWT + Rate Limiting + Audit Logs
Layer 2 : Intelligence Artificielle (Isolation Forest Anomaly Detection)
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from app.extensions import db, limiter
from app.models import User
from app.models.audit import AuditLog
from app.services.anomaly_detector import anomaly_detector


# Helper pour enregistrer dans le journal d'audit avec le Score d'Anomalie IA
def log_audit_event(event_type, login=None, user_id=None, is_success=False):
    try:
        ip = request.remote_addr or '127.0.0.1'
        ua = request.headers.get('User-Agent', '')[:255]
        
        # --- LAYER 2 : Évaluation Comportementale par Machine Learning ---
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
    description='Authentication endpoints with AI Anomaly Detection'
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

        try:
            db.session.add(new_user)
            db.session.commit()
            
            # Audit log de création
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
    @limiter.limit("30 per minute")  # 10 essais / min par IP
    def post(self):
        data = request.get_json() or {}
        login_input = data.get('login')
        password_input = data.get('password')

        if not login_input or not password_input:
            score, is_anomaly = log_audit_event('LOGIN_INVALID_INPUT', login=login_input, is_success=False)
            return {'success': False, 'error': 'Login and password are required'}, 400

        user = User.query.filter_by(login=login_input).first()

        # ÉCHEC DE CONNEXION
        if not user or not user.check_password(password_input):
            score, is_anomaly = log_audit_event('LOGIN_FAILED', login=login_input, user_id=user.id if user else None, is_success=False)
            return {
                'success': False,
                'error': 'Invalid username or password',
                'anomaly_score': score,
                'is_anomaly': is_anomaly
            }, 401

        # COMPTE DÉSACTIVÉ
        if not user.is_active:
            score, is_anomaly = log_audit_event('LOGIN_DISABLED_ACCOUNT', login=login_input, user_id=user.id, is_success=False)
            return {
                'success': False,
                'error': 'Account is disabled',
                'anomaly_score': score,
                'is_anomaly': is_anomaly
            }, 403

        # SUCCÈS DE CONNEXION + ÉVALUATION IA
        score, is_anomaly = log_audit_event('LOGIN_SUCCESS', login=login_input, user_id=user.id, is_success=True)
        
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'login': user.login, 'role': user.role}
        )

        return {
            'success': True,
            'message': f'Welcome {user.full_name}!',
            'access_token': access_token,
            'user': user.to_dict(),
            'anomaly_score': score,       # ← ENVOYÉ À ANGULAR
            'is_anomaly': is_anomaly     # ← ENVOYÉ À ANGULAR
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
