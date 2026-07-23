"""
Routes d'authentification.

Ce module contient tous les endpoints liés à l'authentification :
- POST /api/auth/register : Créer un nouveau compte utilisateur
- POST /api/auth/login    : Se connecter avec des identifiants

Note : Cette version est SIMPLIFIÉE (sans bcrypt/JWT).
La sécurité sera ajoutée dans l'ÉTAPE 20.
"""
from flask import request
from flask_restx import Namespace, Resource, fields

from app.extensions import db
from app.models import User


# ============================================
# NAMESPACE (équivalent d'un Blueprint)
# ============================================
auth_ns = Namespace(
    'auth',
    description='Authentication endpoints (register, login)'
)


# ============================================
# MODÈLES SWAGGER (pour la documentation)
# ============================================
# Ces modèles décrivent le format attendu dans Swagger

register_model = auth_ns.model('RegisterRequest', {
    'first_name': fields.String(
        required=True,
        description='First name of the user',
        example='Ahmed'
    ),
    'last_name': fields.String(
        required=True,
        description='Last name of the user',
        example='Ben Ali'
    ),
    'email': fields.String(
        required=True,
        description='Email address (must be unique)',
        example='ahmed@test.com'
    ),
    'login': fields.String(
        required=True,
        description='Username (must be unique)',
        example='ahmed'
    ),
    'password': fields.String(
        required=True,
        description='Password (will be hashed in production)',
        example='ahmed123'
    ),
    'role': fields.String(
        required=False,
        description='User role (admin, tester, viewer)',
        default='viewer',
        example='viewer'
    )
})

login_model = auth_ns.model('LoginRequest', {
    'login': fields.String(
        required=True,
        description='Username',
        example='ahmed'
    ),
    'password': fields.String(
        required=True,
        description='Password',
        example='ahmed123'
    )
})

user_response_model = auth_ns.model('UserResponse', {
    'id': fields.Integer(description='User ID'),
    'first_name': fields.String(description='First name'),
    'last_name': fields.String(description='Last name'),
    'email': fields.String(description='Email'),
    'login': fields.String(description='Username'),
    'role': fields.String(description='Role'),
    'is_active': fields.Boolean(description='Active status'),
    'created_at': fields.String(description='Creation date')
})


# ============================================
# ENDPOINT : REGISTER
# ============================================
@auth_ns.route('/register')
class Register(Resource):
    """Endpoint pour créer un nouveau compte utilisateur."""
    
    @auth_ns.expect(register_model, validate=False)
    @auth_ns.doc('register_user')
    def post(self):
        """
        Créer un nouveau compte utilisateur.
        
        Vérifie que :
        - Tous les champs obligatoires sont présents
        - L'email n'est pas déjà utilisé
        - Le login n'est pas déjà utilisé
        
        Returns:
            201 : Utilisateur créé avec succès
            400 : Champs manquants ou invalides
            409 : Email ou login déjà utilisé
        """
        # === RÉCUPÉRER LES DONNÉES ENVOYÉES ===
        data = request.get_json()
        
        # === VALIDATION : Champs obligatoires ===
        required_fields = ['first_name', 'last_name', 'email', 'login', 'password']
        
        for field in required_fields:
            if field not in data or not data[field]:
                return {
                    'success': False,
                    'error': f'Missing or empty field: {field}'
                }, 400
        
        # === VÉRIFIER QUE L'EMAIL N'EXISTE PAS ===
        existing_email = User.query.filter_by(email=data['email']).first()
        if existing_email:
            return {
                'success': False,
                'error': 'Email already registered'
            }, 409  # 409 = Conflict
        
        # === VÉRIFIER QUE LE LOGIN N'EXISTE PAS ===
        existing_login = User.query.filter_by(login=data['login']).first()
        if existing_login:
            return {
                'success': False,
                'error': 'Login already taken'
            }, 409
        
        # === CRÉER LE NOUVEL UTILISATEUR ===
        new_user = User(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            login=data['login'],
            password=data['password'],  # ⚠️ En clair pour l'instant !
            role=data.get('role', 'viewer')  # Par défaut : viewer
        )
        
        # === SAUVEGARDER DANS LA BD ===
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f'Database error: {str(e)}'
            }, 500
        
        # === RETOURNER LA RÉPONSE ===
        return {
            'success': True,
            'message': 'User created successfully',
            'user': new_user.to_dict()
        }, 201  # 201 = Created


# ============================================
# ENDPOINT : LOGIN
# ============================================
@auth_ns.route('/login')
class Login(Resource):
    """Endpoint pour se connecter avec des identifiants."""
    
    @auth_ns.expect(login_model, validate=False)
    @auth_ns.doc('login_user')
    def post(self):
        """
        Se connecter avec un login et un mot de passe.
        
        Vérifie que :
        - Le login et le password sont fournis
        - L'utilisateur existe
        - Le mot de passe correspond
        
        Returns:
            200 : Connexion réussie
            400 : Champs manquants
            401 : Identifiants invalides
        """
        # === RÉCUPÉRER LES DONNÉES ===
        data = request.get_json()
        
        # === VALIDATION : Champs obligatoires ===
        if not data or 'login' not in data or 'password' not in data:
            return {
                'success': False,
                'error': 'Login and password are required'
            }, 400
        
        # === CHERCHER L'UTILISATEUR ===
        user = User.query.filter_by(login=data['login']).first()
        
        # === VÉRIFIER QUE L'UTILISATEUR EXISTE ===
        if not user:
            return {
                'success': False,
                'error': 'Invalid username or password'
            }, 401  # 401 = Unauthorized
        
        # === VÉRIFIER LE MOT DE PASSE (en clair pour l'instant) ===
        if user.password != data['password']:
            return {
                'success': False,
                'error': 'Invalid username or password'
            }, 401
        
        # === VÉRIFIER QUE LE COMPTE EST ACTIF ===
        if not user.is_active:
            return {
                'success': False,
                'error': 'Account is disabled'
            }, 403  # 403 = Forbidden
        
        # === RÉPONSE DE SUCCÈS ===
        return {
            'success': True,
            'message': f'Welcome {user.full_name}!',
            'user': user.to_dict()
        }, 200