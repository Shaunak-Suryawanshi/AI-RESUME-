"""Authentication and authorization helpers."""
from flask import abort
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models.user import User


def get_current_user() -> User:
    """Return the user represented by the already-validated JWT."""
    identity = get_jwt_identity()
    try:
        user_id = int(identity)
    except (TypeError, ValueError):
        abort(401, description="Invalid token identity")
    user = db.session.get(User, user_id)
    if user is None:
        abort(401, description="User for this token no longer exists")
    return user


def get_owned_or_404(model, resource_id: int, user_id: int):
    """Fetch a private resource only when it belongs to the authenticated user."""
    resource = db.session.get(model, resource_id)
    if resource is None or resource.user_id != user_id:
        abort(404, description="Resource not found")
    return resource
