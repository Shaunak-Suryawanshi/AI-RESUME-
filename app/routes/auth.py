from flask import Blueprint, request
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from app.schemas.user import UserRegister, UserLogin
from app.extensions import db
from app.models.user import User
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required
from app.services.auth import get_current_user

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return {"error": "No input data provided"}, 400

    try:
        user_data = UserRegister(**data)
    except ValidationError as error:
        return{
            "error": "Invalid input data",
            "details": error.errors()
        }, 400

    password_hash = generate_password_hash(user_data.password)

    user = User(
        name=user_data.name,
        email=str(user_data.email),
        password_hash=password_hash,
        bio=user_data.bio
    )

    try:
        db.session.add(user)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()

        return{
            "error": "Email already exists"
        },409

    return{
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "bio": user.bio
    }, 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return {"error": "No input data provided"}, 400

    try:
        user_data = UserLogin(**data)
    except ValidationError as error:
        return {
            "error": "Invalid input data",
            "details": error.errors()
        }, 400

    user = db.session.execute(
        db.select(User).where(
            User.email == str(user_data.email)
        )
    ).scalar_one_or_none()

    if user is None:
        return {
            "error": "Invalid email or password"
        }, 401

    if not check_password_hash(
        user.password_hash,
        user_data.password
    ):
        return {
            "error": "Invalid email or password"
        }, 401

    identity = str(user.id)
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    return {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }, 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Exchange a valid refresh token for a new short-lived access token."""
    user = get_current_user()
    return {"access_token": create_access_token(identity=str(user.id))}, 200
