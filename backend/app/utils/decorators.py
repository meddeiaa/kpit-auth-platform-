"""
Décorateurs d'autorisation (RBAC) — Layer 1 SECURITY+.

À utiliser APRÈS @jwt_required() sur les routes Flask-RESTX.
Le rôle lu vient du JWT signé (additional_claims), pas du client.
"""
from functools import wraps

from flask_jwt_extended import get_jwt


def roles_required(*allowed_roles):
    """
    Autorise la route seulement si claims['role'] est dans allowed_roles.

    Exemple :
        @jwt_required()
        @roles_required('admin')
        def delete(...):
            ...

        @jwt_required()
        @roles_required('admin', 'tester')
        def run(...):
            ...
    """
    allowed = tuple(r.lower() for r in allowed_roles)

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            claims = get_jwt() or {}
            role = (claims.get('role') or '').lower()

            if role not in allowed:
                return {
                    'success': False,
                    'error': (
                        'Forbidden: insufficient role. '
                        f'Required: {", ".join(allowed)}; got: {role or "unknown"}'
                    ),
                }, 403

            return fn(*args, **kwargs)

        return wrapper

    return decorator