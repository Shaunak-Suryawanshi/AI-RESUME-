from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.extensions import db
from pydantic import ValidationError
from app.schemas.user import UserUpdate
from app.services.auth import get_current_user

users_bp = Blueprint("users", __name__, url_prefix="/api/users")

def serialize_user(user):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "bio": user.bio
    }

@users_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    return serialize_user(get_current_user()), 200


@users_bp.route("/me", methods=["PATCH"])
@jwt_required()
def update_me():
    data = request.get_json(silent=True)
    if not data:
        return {"error": "No input data provided"}, 400
    try:
        update_data = UserUpdate(**data)
    except ValidationError as error:
        return {"error": "Invalid input data", "details": error.errors()}, 400
    user = get_current_user()
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.session.commit()
    return serialize_user(user), 200
