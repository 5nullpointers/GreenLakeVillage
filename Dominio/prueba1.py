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

# Conectar a MongoDB
mongo_agent = MongoDBAgent()
# Verificar la conexión
if not mongo_agent.client:
    print("❌ Error al conectar con MongoDB")
    exit(1)
else:
    # print("✅ Conexión a MongoDB establecida correctamente")
    pass
    
@app.route('/api/retos/marcar_notificado', methods=['POST'])
def marcar_reto_notificado():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401
    
    reto_id = request.json.get("reto_id")
    if not reto_id:
        return jsonify({"error": "Reto id no proporcionado"}), 400

    try:
        result = mongo_agent.db["usuarios"].update_one(
            {
                "_id": ObjectId(user_id),
                "retos_completados.reto_id": reto_id
            },
            {
                "$set": {"retos_completados.$.popup_mostrado": True}
            }
        )
        if result.modified_count > 0:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "No se pudo actualizar el reto."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Configuración para archivos
UPLOAD_FOLDER = os.path.join(STATIC_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/retos_pendientes', methods=['GET'])
def api_retos_pendientes():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    try:
        usuario = mongo_agent.db["usuarios"].find_one({"_id": ObjectId(user_id)})
    except Exception as e:
        return jsonify({"error": "Error al obtener el usuario"}), 500

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    retos_pendientes = []
    # Solo se consideran los retos completados (es decir, que existen en el arreglo)
    # y que no han sido notificados (popup_mostrado: False)
    retos_completados = usuario.get("retos_completados", [])
    for registro in retos_completados:
        if not registro.get("popup_mostrado", False):
            reto_id = registro["reto_id"]
            reto_info = mongo_agent.db["retos"].find_one({"_id": ObjectId(reto_id)})
            if reto_info:
                retos_pendientes.append({
                    "id": str(reto_info["_id"]),
                    "nombre": reto_info.get("name"),
                    "descripcion": reto_info.get("descripcion"),
                    "tokens": reto_info.get("tokens")
                })

    return jsonify(retos_pendientes)

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/descubrir')
def descubrir():
    return render_template('descubrir.html')

@app.route('/api/hoteles')
def api_hoteles():
    """
    Retorna un JSON con todos los hoteles guardados en MongoDB.
    """
    hoteles = list(mongo_agent.db["hoteles"].find({}))
    
    # Convertir ObjectId a string para no tener problemas al serializar
    for h in hoteles:
        h["_id"] = str(h["_id"])
    
    return jsonify(hoteles)

@app.route('/api/rutas')
def api_rutas():
    """
    Retorna un JSON con todas las rutas turísticas guardadas en MongoDB.
    """
    rutas = list(mongo_agent.db["rutas_turisticas"].find({}))
    for r in rutas:
        r["_id"] = str(r["_id"])  # Convertir ObjectId a string
    return jsonify(rutas)

@app.route('/api/restaurantes')
def api_restaurantes():
    """
    Retorna un JSON con todos los restaurantes guardados en MongoDB.
    """
    restaurantes = list(mongo_agent.db["restaurantes"].find({}))

    #Convertir ObjectId a string para no tener problemas al serializar
    for r in restaurantes:
        r["_id"] = str(r["_id"])

    return jsonify(restaurantes)

MAX_HISTORY = 5
conversation_history = []

@app.route('/api/ratings')
def api_ratings():
    """
    Retorna un JSON con la media de puntuación y el número de opiniones
    para cada hotel, con el nombre del servicio como clave.
    """
    agregados = OpinionesTuristicasDAO.obtener_agregados()
    # Convertir la lista a un diccionario, ej.:
    # {
    #    "Alletra Boutique Hotel": { "media_puntuacion": 4.3, "numero_comentarios": 12 },
    #    ...
    # }
    ratings_dict = {
        entry["_id"]: {
            "media_puntuacion": entry["media_puntuacion"],
            "numero_comentarios": entry["numero_comentarios"]
        }
        for entry in agregados
    }
    return jsonify(ratings_dict)

@app.route('/hoteles/<string:hotel_id>')
def hotel_detalle(hotel_id):
    """
    Muestra una página con más detalles de un hotel, incluyendo la sección de opiniones.
    """
    try:
        obj_id = ObjectId(hotel_id)
    except:
        return abort(400, description="ID inválido")

    hotel = mongo_agent.db["hoteles"].find_one({"_id": obj_id})
    if not hotel:
        return abort(404, description="Hotel no encontrado")
    hotel["_id"] = str(hotel["_id"])

    # Obtener opiniones y la media de la puntuación mediante el DAO
    opiniones, avg_rating = OpinionesTuristicasDAO.obtener_opiniones_y_media(hotel["nombre"])

    return render_template('hotel_detalles.html', hotel=hotel, opiniones=opiniones, avg_rating=avg_rating)

@app.template_filter('format_number')
def format_number(value):
    try:
        value = float(value)
        if value >= 1000000:
            # Divide entre 1.000.000 y muestra dos decimales seguidos de "M"
            return f"{value/1000000:.2f} Millones de"
        else:
            # Muestra el número con separadores de miles (puntos)
            return f"{value:,.0f}".replace(",", ".")
    except Exception:
        return value

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

@app.template_filter('short_number')
def short_number(value):
    """
    Devuelve un número en formato abreviado:
      1,200 => "1.20K"
      8793114 => "8.79M"
    """
    try:
        num = float(value)
        if num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.2f}B"
        elif num >= 1_000_000:
            return f"{num / 1_000_000:.2f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.2f}K"
        else:
            return str(int(num))
    except:
        return str(value)

def registrar_reto(usuario, reto_id):
    reto_info = mongo_agent.db["retos"].find_one({"_id": ObjectId(reto_id)})
    if not reto_info:
        return

    # Si ya se registró (sin importar el flag), no volvemos a registrar
    retos_completados = usuario.get("retos_completados", [])
    if any(str(r["reto_id"]) == reto_id for r in retos_completados):
        return

    nuevo_reto = {
        "reto_id": reto_id,
        "fecha": datetime.utcnow(),
        "popup_mostrado": False
    }
    mongo_agent.db["usuarios"].update_one(
        {"_id": usuario["_id"]},
        {
            "$push": {"retos_completados": nuevo_reto},
            "$inc": {"tokens": reto_info.get("tokens", 0)}
        }
    )

# Función auxiliar para predecir con regresión lineal simple
def forecast_series(values, forecast_horizon):
    """
    Realiza una predicción simple usando regresión lineal sobre la serie de datos.
    Si hay menos de 2 datos, retorna el último valor repetido 'forecast_horizon' veces.
    """
    n = len(values)
    if n < 2:
        return [values[-1]] * forecast_horizon
    x = np.arange(n)
    # Ajuste lineal: y = a*x + b
    a, b = np.polyfit(x, values, 1)
    predictions = []
    for i in range(1, forecast_horizon + 1):
        pred = a * (n - 1 + i) + b
        predictions.append(pred)
    return predictions

if __name__ == '__main__':
    # Escucha en todas las IPs (0.0.0.0) y puerto 5000
    app.run(host='0.0.0.0', port=5000, debug=True)