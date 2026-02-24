from flask import Flask
from config import Config
from models import db
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)

# Inicializar base de datos
db.init_app(app)

# Configurar LoginManager
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "info"
login_manager.init_app(app)

# 👇 IMPORTANTE: crear tablas en PostgreSQL
with app.app_context():
    db.create_all()

# Importar rutas después de crear app
from routes import *

if __name__ == "__main__":
    app.run()