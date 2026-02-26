
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
    dias_vacaciones = db.Column(db.Integer, default=12)

from datetime import datetime

class Vacacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref="vacaciones")

    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)

    dias_solicitados = db.Column(db.Integer)

    estado = db.Column(db.String(20), default="Pendiente")  
    # Pendiente / Aprobado / Rechazado

    created_at = db.Column(db.DateTime, default=datetime.utcnow)