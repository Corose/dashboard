
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class AuthUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(20))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    usuario = db.Column(db.String(150), nullable=False)
    correo = db.Column(db.String(150), nullable=False)
    equipo = db.Column(db.String(100), nullable=False)
    jefe = db.Column(db.String(150))
    accesos = db.Column(db.String(500))
    comentarios = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.now())
    activo = db.Column(db.Boolean, default=True)
