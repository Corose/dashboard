from flask import Flask
from config import Config
from models import db, AuthUser
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "info"
login_manager.init_app(app)

from routes import *

# 🔥 CREAR TABLAS Y ADMIN
with app.app_context():
    db.create_all()

    if not AuthUser.query.filter_by(username="admin").first():
        admin = AuthUser(
            username="admin",
            password=generate_password_hash("admin123"),
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin auto-creado")

if __name__ == "__main__":
    app.run()