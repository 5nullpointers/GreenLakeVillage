import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime

import numpy as np
import openai
from dotenv import load_dotenv

from flask import Flask, render_template, request, jsonify, session, abort
from flask.json.provider import DefaultJSONProvider

from bson.objectid import ObjectId
from bson import ObjectId

from Persistencia.DAOS.OpinionesTuristicasDAO import OpinionesTuristicasDAO
from Persistencia.AgenteBD import MongoDBAgent

from admin import admin_bp
from propietarios import propietarios_bp
from reservas import reservas_bp
from auth import auth_bp
from forum import forum_bp
from maps import maps_bp
from retos import retos_bp
from turismo import turismo_bp

from Entidades.asistenteIA import obtener_respuesta

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

app = Flask(__name__,
            template_folder=TEMPLATE_DIR,
            static_folder=STATIC_DIR)
app.json_provider_class = CustomJSONProvider
app.json = app.json_provider_class(app)

# Configurar clave secreta para sesiones y mensajes flash
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Clave de la API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Archivo admin
app.register_blueprint(admin_bp, url_prefix='/admin')
# Archivo propietarios
app.register_blueprint(propietarios_bp, url_prefix='/propietarios')
# Archivo reservas
app.register_blueprint(reservas_bp, url_prefix='/reservas')
# Archivo auth y users
app.register_blueprint(auth_bp)
# Archivo forum
app.register_blueprint(forum_bp)
# Archivo maps y navegación
app.register_blueprint(maps_bp)
# Archivo retos
app.register_blueprint(retos_bp, url_prefix='/api/retos')
# Archivo turismo
app.register_blueprint(turismo_bp)

# Conectar a MongoDB
mongo_agent = MongoDBAgent()
# Verificar la conexión
if not mongo_agent.client:
    print("❌ Error al conectar con MongoDB")
    exit(1)
else:
    # print("✅ Conexión a MongoDB establecida correctamente")
    pass

# Configuración para archivos
UPLOAD_FOLDER = os.path.join(STATIC_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/descubrir')
def descubrir():
    return render_template('descubrir.html')

MAX_HISTORY = 5
conversation_history = []

@app.route('/chat', methods=['POST'])
def chat_page():
    # Obtener el identificador del usuario de la sesión
    user_identifier = session.get("user_id")
    if not user_identifier:
        return jsonify({"error": "Usuario no autenticado"}), 401

    # Intentar obtener el usuario usando _id si user_identifier es un ObjectId en forma de cadena
    try:
        usuario = mongo_agent.db["usuarios"].find_one({"_id": ObjectId(user_identifier)})
        if usuario:
            user_email = usuario.get("email")
        else:
            user_email = None
    except Exception as e:
        # Si falla la conversión, asumimos que ya es un email
        user_email = user_identifier

    if not user_email:
        return jsonify({"error": "No se pudo recuperar el correo del usuario"}), 401

    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"error": "Mensaje vacío"}), 400

    try:
        # Llama a la función que construye el prompt usando los datos del usuario desde la BBDD
        response = obtener_respuesta(user_email, user_message)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Escucha en todas las IPs (0.0.0.0) y puerto 5000
    app.run(host='0.0.0.0', port=5000, debug=True)