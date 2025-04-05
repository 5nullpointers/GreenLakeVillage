import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import openai
from dotenv import load_dotenv
from flask import Flask
from flask.json.provider import DefaultJSONProvider
from bson.objectid import ObjectId

from Persistencia.AgenteBD import MongoDBAgent

from admin import admin_bp
from propietarios import propietarios_bp
from reservas import reservas_bp
from auth import auth_bp
from forum import forum_bp
from maps import maps_bp
from retos import retos_bp
from turismo import turismo_bp
from general import general_bp
from Dominio.utils import format_number

dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path)

# --- Codificador JSON personalizado ---
class CustomJSONProvider(DefaultJSONProvider):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)
# ------------------------------------

# Calcula la ruta absoluta a /Presentacion/templates
BASE_DIR = os.path.dirname(__file__)         # => Dominio/
TEMPLATE_DIR = os.path.join(BASE_DIR, '..', 'Presentacion', 'templates')
STATIC_DIR = os.path.join(BASE_DIR, '..', 'Presentacion', 'static')

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.json_provider_class = CustomJSONProvider
app.json = app.json_provider_class(app)
app.json_provider_class = CustomJSONProvider
# Registrar el filtro en Jinja2
app.jinja_env.filters['format_number'] = format_number
# Configurar clave secreta para sesiones y mensajes flash
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Clave de la API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Registrar blueprints
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(propietarios_bp, url_prefix='/propietarios')
app.register_blueprint(reservas_bp, url_prefix='/reservas')
app.register_blueprint(auth_bp)
app.register_blueprint(forum_bp)
app.register_blueprint(maps_bp)
app.register_blueprint(retos_bp, url_prefix='/api/retos')
app.register_blueprint(turismo_bp)
app.register_blueprint(general_bp)

# Conectar a MongoDB
mongo_agent = MongoDBAgent()
if not mongo_agent.client:
    print("Error al conectar con MongoDB")
    exit(1)

if __name__ == '__main__':
    # Escucha en todas las IPs (0.0.0.0) y puerto 5000
    app.run(host='0.0.0.0', port=5000, debug=True)