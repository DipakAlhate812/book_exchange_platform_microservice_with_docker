from db import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        # self.password_hash = (password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Token(db.Model):
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), db.ForeignKey('users.email'), nullable=False)
    token = db.Column(db.String(250), nullable=True)
    refresh_token = db.Column(db.String(250), nullable=True)
    otp = db.Column(db.String(6), nullable=True)  # 6-digit OTP
    otp_expires_at = db.Column(db.DateTime, nullable=True)  # Expiration time for OTP
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=True)  # Optional field for token expiration (e.g., JWT token)

    user = db.relationship('User', backref=db.backref('tokens', lazy=True))

