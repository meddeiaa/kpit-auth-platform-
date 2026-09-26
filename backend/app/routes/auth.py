"""
Routes d'authentification.

Layer 0 : register + login
Layer 1A : bcrypt
Layer 1B : JWT access_token au login + GET /auth/me
"""
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)

from app.extensions import db,limiter
from app.models import User
from app.models.audit import AuditLog


auth_ns = Namespace(
    'auth',
    description='Authentication endpoints (register, login, me)'
)


register_model = auth_ns.model('RegisterRequest', {
    'first_name': fields.String(required=True, example='Ahmed'),
    'last_name': fields.String(required=True, example='Ben Ali'),
    'email': fields.String(required=True, example='ahmed@test.com'),
    'login': fields.String(required=True, example='ahmed'),
    'password': fields.String(required=True, example='ahmed123'),
    'role': fields.String(required=False, default='viewer', example='viewer'),
})

login_model = auth_ns.model('LoginRequest', {
    'login': fields.String(required=True, example='ahmed'),
    'password': fields.String(required=True, example='ahmed123'),
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
            role=data.get('role', 'viewer') or 'viewer',
        )
        new_user.set_password(data['password'])

        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Database error: {str(e)}'}, 500

        return {
            'success': True,
            'message': 'User created successfully',
            'user': new_user.to_dict(),
        }, 201

def log_audit_event(event_type, login=None, user_id=None):
    try:
        log_entry = AuditLog(
            user_id=user_id,
            login_attempted=login,
            event=event_type,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:255]
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"[AUDIT LOG ERROR] {e}")

@auth_ns.route('/login')
class Login(Resource):
    """Endpoint pour se connecter avec des identifiants."""
    
    @auth_ns.expect(login_model, validate=False)
    @auth_ns.doc('login_user')
    @limiter.limit("5 per minute")  # ← PROTECTION ANTI BRUTE-FORCE : 5 essais/min par IP
    def post(self):
        data = request.get_json() or {}
        login_input = data.get('login')
        password_input = data.get('password')

        if not login_input or not password_input:
            log_audit_event('LOGIN_INVALID_INPUT', login=login_input)
            return {'success': False, 'error': 'Login and password are required'}, 400

        user = User.query.filter_by(login=login_input).first()

        # ÉCHEC DE CONNEXION (Mot de passe faux ou utilisateur inexistant)
        if not user or not user.check_password(password_input):
            log_audit_event('LOGIN_FAILED', login=login_input, user_id=user.id if user else None)
            return {'success': False, 'error': 'Invalid username or password'}, 401

        # COMPTE DÉSACTIVÉ
        if not user.is_active:
            log_audit_event('LOGIN_DISABLED_ACCOUNT', login=login_input, user_id=user.id)
            return {'success': False, 'error': 'Account is disabled'}, 403

        # SUCCÈS DE CONNEXION
        log_audit_event('LOGIN_SUCCESS', login=login_input, user_id=user.id)
        
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'login': user.login, 'role': user.role}
        )

        return {
            'success': True,
            'message': f'Welcome {user.full_name}!',
            'access_token': access_token,
            'user': user.to_dict()
        }, 200


@auth_ns.route('/me')
class Me(Resource):
    """Récupérer le profil de l'utilisateur connecté via son JWT."""
    
    @jwt_required()
    @auth_ns.doc(security='Bearer')  # ← AJOUT ICI (Affiche le cadenas sur GET /me)
    def get(self):
        """Retourne les informations de l'utilisateur identifié par le token."""
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