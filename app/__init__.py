import os
from dotenv import load_dotenv
load_dotenv()
from flask import Flask
from app.config import DevelopmentConfig, ProductionConfig
from app.extensions import db, migrate, jwt
from app.routes.users import users_bp
from app.routes.auth import auth_bp
from app.routes.resumes import resumes_bp
from app.routes.jobs import jobs_bp
from app.routes.analyses import analyses_bp



def create_app():
    app = Flask(__name__)

    environment = os.getenv("FLASK_ENV", "development")

    if environment == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    @jwt.unauthorized_loader
    def missing_token(reason):
        return {"error": "Authentication required", "details": reason}, 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return {"error": "Invalid token", "details": reason}, 422

    @jwt.expired_token_loader
    def expired_token(_jwt_header, _jwt_payload):
        return {"error": "Token has expired"}, 401

    from app import models  # Import models to register them with SQLAlchemy
    from app.routes.main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(resumes_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(analyses_bp)
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Not found"}, 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return {"error": "Method not allowed"}, 405

    @app.errorhandler(500)
    def internal_server_error(error):
        return {"error": "Internal server error"}, 500

    @app.errorhandler(413)
    def file_too_large(error):
        return {"error": "File is too large. Maximum size is 5 MiB"}, 413

    @app.errorhandler(401)
    def unauthorized(error):
        return {"error": error.description or "Authentication required"}, 401

    return app
