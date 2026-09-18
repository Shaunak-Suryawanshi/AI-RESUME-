from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    bio = db.Column(db.String(500), nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    resumes = db.relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    jobs = db.relationship("Job", back_populates="user", cascade="all, delete-orphan")
    analyses = db.relationship("Analysis", back_populates="user", cascade="all, delete-orphan")
