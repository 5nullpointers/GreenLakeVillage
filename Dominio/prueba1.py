import sys
import signal
from dotenv import load_dotenv
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import openai
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from Entidades.RutasTuristicas import RutasTuristicas
from Entidades.OcupacionHotelera import OcupacionHotelera
from Entidades.OpinionesTuristicas import OpinionesTuristicas
from Entidades.Sostenibilidad import Sostenibilidad
from Entidades.UsoTransporte import UsoTransporte
from Persistencia.DAOS.OpinionesTuristicasDAO import OpinionesTuristicasDAO
from Persistencia.DAOS.UserDAO import UserDAO

# --- Codificador JSON personalizado ---
from flask.json.provider import DefaultJSONProvider
from bson import ObjectId

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
# Cargar variables de entorno desde .env
load_dotenv()

# Clave de la API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

from werkzeug.security import generate_password_hash, check_password_hash

# Conectar a MongoDB
from Persistencia.AgenteBD import MongoDBAgent
from Persistencia.DAOS.RutasTuristicasDAO import RutasTuristicasDAO
from Persistencia.DAOS.OcupacionHoteleraDAO import OcupacionHoteleraDAO
from Persistencia.DAOS.OpinionesTuristicasDAO import OpinionesTuristicasDAO
from Persistencia.DAOS.SostenibilidadDAO import SostenibilidadDAO
from Persistencia.DAOS.UsoTransporteDAO import UsoTransporteDAO
mongo_agent = MongoDBAgent()
# Verificar la conexión
if not mongo_agent.client:
    print("❌ Error al conectar con MongoDB")
    exit(1)
else:
    # print("✅ Conexión a MongoDB establecida correctamente")
    pass

# prueba1.py (fragmento)

import os
import requests
from flask import Flask, request, jsonify, render_template


# Clave de servidor para la Routes API v2
# (¡No la expongas en el frontend!)
ROUTES_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

@app.route("/get-route", methods=["POST"])
def get_route():
    """
    Recibe { origin: {latitude, longitude}, destination: {latitude, longitude} }
    Llama a la Routes API v2 y devuelve la polyline
    """
    data = request.json
    origin = data.get("origin")
    destination = data.get("destination")

    if not origin or not destination:
        return jsonify({"error": "Origin/destination missing"}), 400

    # Construir el payload para la nueva Routes API v2
    payload = {
        "origin": {"location": {"latLng": origin}},
        "destination": {"location": {"latLng": destination}},
        "travelMode": "DRIVE"
    }

    # Llamar a la Routes API
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": ROUTES_API_KEY,
        "X-Goog-FieldMask": "routes.polyline.encodedPolyline"
    }
    url = "https://routes.googleapis.com/directions/v2:computeRoutes"

    try:
        resp = requests.post(url, json=payload, headers=headers)
        resp_data = resp.json()
        return jsonify(resp_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/map")
def map_page():
    # En lugar de usar un valor por defecto, tomamos la clave de .env
    google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    return render_template("map.html", google_maps_api_key=google_maps_api_key)


@app.route('/')
def index():
    # Lo mismo para el index
    google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    return render_template('index.html', google_maps_api_key=google_maps_api_key)


@app.route('/users', methods=['GET'])
def users():
    usuarios = UserDAO.obtener_todos()
    return jsonify(usuarios), 200

# Metodo para bloquear al usuario
@app.route('/admin/blockUser', methods=['POST'])
def block_user():
    data = request.get_json()
    user_id = data.get("id")
    if not user_id:
        return jsonify({"error": "ID de usuario no proporcionado."}), 400
    try:
        from bson import ObjectId
        # Actualizar directamente en la colección "users"
        result = mongo_agent.db['usuarios'].update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"blocked": True}}
        )
        if result.modified_count > 0:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "No se pudo actualizar el usuario."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Metodo para desbloquear al usuario
@app.route('/admin/unblockUser', methods=['POST'])
def unblock_user():
    data = request.get_json()
    user_id = data.get("id")
    if not user_id:
        return jsonify({"error": "ID de usuario no proporcionado."}), 400
    try:
        from bson import ObjectId
        result = mongo_agent.db['usuarios'].update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"blocked": False}}
        )
        if result.modified_count > 0:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "No se pudo actualizar el usuario."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Nuevo endpoint para eliminar un usuario
@app.route('/admin/deleteUser', methods=['POST'])
def delete_user():
    data = request.get_json()
    user_id = data.get("id")
    if not user_id:
        return jsonify({"error": "ID de usuario no proporcionado."}), 400
    try:
        from bson import ObjectId
        result = UserDAO.borrar_dato({"_id": ObjectId(user_id)})
        if result.deleted_count > 0:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "No se pudo eliminar el usuario."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/map')
def map():
    google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    return render_template('map.html', google_maps_api_key=google_maps_api_key)


@app.route('/login')
def login_page():
    # Ahora la ruta '/login' redirige a loginRegister.html
    return render_template('loginRegister.html')

@app.route('/MapaAdmin')
def MapaAdmin():
    return render_template('MapaAdmin.html')

@app.route('/admin/UsuariosAdmin')
def UsuariosAdmin():
    return render_template('UsuariosAdmin.html')

@app.route('/admin')
def admin():
    from Persistencia.DAOS.OcupacionHoteleraDAO import OcupacionHoteleraDAO
    from Persistencia.DAOS.HotelesDAO import HotelesDAO
    from Persistencia.DAOS.SostenibilidadDAO import SostenibilidadDAO

    consumo_total = SostenibilidadDAO.obtener_Consumo()
    totalReservas = OcupacionHoteleraDAO.UsuariosTotales()
    hoteles = HotelesDAO.obtener_precios()
    ocupaciones = list(mongo_agent.db["ocupacion_hotelera"].find({}, {"hotel_nombre": 1, "reservas_confirmadas": 1}))
    
    # Depuración: ver qué se obtiene de ocupaciones
    # print("Datos de ocupaciones:", ocupaciones)
    
    # Agrupar reservas por hotel y convertir reservas a número si es necesario
    ocup_dict = {}
    for o in ocupaciones:
        nombre_occ = o.get("hotel_nombre")
        reservas = o.get("reservas_confirmadas", 0)
        if isinstance(reservas, str):
            try:
                reservas = int(reservas)
            except Exception:
                reservas = 0
        ocup_dict[nombre_occ] = ocup_dict.get(nombre_occ, 0) + reservas
    # print("Diccionario de ocupaciones:", ocup_dict)
    
    # Calcular ingresos totales: convertir precio a numérico si es cadena
    ingresos_totales = 0
    for h in hoteles:
        hotel_nombre = h.get("nombre")
        precio = h.get("precio", 0)
        if isinstance(precio, str):
            try:
                precio = float(precio)
            except Exception:
                precio = 0
        ingreso = precio * ocup_dict.get(hotel_nombre, 0)
        # print("Hotel:", hotel_nombre, "Precio:", precio, "Reservas:", ocup_dict.get(hotel_nombre, 0), "Ingreso:", ingreso)
        ingresos_totales += ingreso
    return render_template('Admin.html', ingresosTotales=ingresos_totales, totalReservas=totalReservas, consumoTotal=consumo_total)

@app.route('/UserBlock')
def UserBlock():
    return render_template('UserBlocked.html')

@app.route('/admin/editUser', methods=['POST'])
def edit_user():
    data = request.get_json()
    try:
        user_id = data.get("_id")
        if not user_id:
            return jsonify({"success": False, "error": "Missing user _id"})
        filtro = {"_id": ObjectId(user_id)}
        update_data = {
            "name": data.get("name"),
            "email": data.get("email"),
            "type": data.get("type")
        }
        result = UserDAO.actualizar_dato(filtro, update_data)
        if result.modified_count > 0:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "No se actualizó ningún registro"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    # blocked = request.form.get('blocked')

    if not email or not password:
        flash("Por favor, completa ambos campos.")
        return redirect(url_for('login_page'))

    usuario = UserDAO.obtener_dato({"email": email})
    if usuario:
        if usuario.get("blocked") == True:
            return redirect(url_for('UserBlock'))

        if usuario.get("type") != "Admin":
            # Si ya se almacena la contraseña hasheada, usamos check_password_hash
            if check_password_hash(usuario.get("pass"), password):
                session['user_id'] = str(usuario["_id"])
                session['user_name'] = usuario.get("name")
                flash("Inicio de sesión exitoso!")
                return redirect(url_for('map'))
            else:
                flash("Contraseña incorrecta.")
                return redirect(url_for('login_page'))
        else:
             # Si ya se almacena la contraseña hasheada, usamos check_password_hash
            if check_password_hash(usuario.get("pass"), password):
                session['user_id'] = str(usuario["_id"])
                session['user_name'] = usuario.get("name")
                flash("Inicio de sesión exitoso!")
                return redirect(url_for('admin'))
            else:
                flash("Contraseña incorrecta.")
                return redirect(url_for('login_page'))
    else:
        flash("Usuario no encontrado.")
        return redirect(url_for('login_page'))

# Ruta de registro: procesar formulario de registro
@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    blocked = False

    if not name or not email or not password:
        flash("Todos los campos son obligatorios.")
        return redirect(url_for('login_page'))

    # Verificar si el usuario ya existe
    if UserDAO.obtener_dato({"email": email}):
        flash("El correo ya está registrado.")
        return redirect(url_for('login_page'))

    # Hashear la contraseña antes de guardarla
    hashed_password = generate_password_hash(password)
    nuevo_usuario = {
        "name": name,
        "email": email,
        "pass": hashed_password,
        "type": "Tourist",  # o asignar otro tipo según corresponda
        "blocked": blocked
    }

    UserDAO.insertar_dato(nuevo_usuario)
    flash("Registro exitoso. Ahora puedes iniciar sesión.")
    return redirect(url_for('login_page'))


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

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message")

    if not user_message:
        return jsonify({"error": "Mensaje vacío"}), 400

    try:
        client = openai.OpenAI()

        # Agregar el nuevo mensaje al historial
        conversation_history.append({"role": "user", "content": user_message})

        # Limitar el historial solo a los últimos MAX_HISTORY mensajes
        # Multiplicamos por 2 porque cada mensaje tiene respuesta de la IA
        conversation_history_trimmed = conversation_history[-(MAX_HISTORY * 2):]

        # Crear el mensaje con el historial recortado
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "Eres un asistente virtual para facilitar ayuda turística de rutas y hoteles..."}] + conversation_history_trimmed
        )

        chat_response = response.choices[0].message.content

        # Agregar la respuesta de la IA al historial
        conversation_history.append({"role": "assistant", "content": chat_response})

        return jsonify({"response": chat_response})

    except openai.OpenAIError as e:
        return jsonify({"error": f"Error en OpenAI: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error desconocido: {str(e)}"}), 500

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

from bson import ObjectId
from flask import render_template, abort

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
            return f"{value/1000000:.2f}Millones de"
        else:
            # Muestra el número con separadores de miles (puntos)
            return f"{value:,.0f}".replace(",", ".")
    except Exception:
        return value

@app.route('/api/estadisticas_ocupacion')
def api_estadisticas_ocupacion():
    ocupaciones = OcupacionHoteleraDAO.obtener_todos()
    if not ocupaciones:
        # Si no hay datos, devolvemos ceros
        return jsonify({
            "tasa_ocupacion_users": 0,
            "tasa_ocupacion_percent": 0,
            "reservas_confirmadas": 0,
            "reservas_percent": 0,
            "cancelaciones": 0,
            "cancelaciones_percent": 0
        })

    # 1) Calcular totales
    total_reservas = sum(o["reservas_confirmadas"] for o in ocupaciones)
    total_cancelaciones = sum(o["cancelaciones"] for o in ocupaciones)
    total_usuarios = total_reservas + total_cancelaciones

    # 2) Calcular promedios
    total_tasa = sum(o["tasa_ocupacion"] for o in ocupaciones)  # suma de % ocupacion
    promedio_tasa = round(total_tasa / len(ocupaciones), 3)     # promedio de % ocupacion

    # 3) Convertir “tasa de ocupación” (porcentaje) a número de usuarios
    #    Ej.: 50% de 200 usuarios => 100 usuarios
    if total_usuarios > 0:
        ocupacion_users = round((promedio_tasa / 100) * total_usuarios)
    else:
        ocupacion_users = 0

    # 4) Calcular porcentajes de reservas y cancelaciones sobre el total
    #    (si total_usuarios=0, evitamos división por cero)
    if total_usuarios > 0:
        reservas_percent = round((total_reservas / total_usuarios) * 100, 3)
        cancelaciones_percent = round((total_cancelaciones / total_usuarios) * 100, 3)
    else:
        reservas_percent = 0
        cancelaciones_percent = 0

    return jsonify({
        "tasa_ocupacion_users": ocupacion_users,
        "tasa_ocupacion_percent": promedio_tasa,        # ← con 3 decimales
        "reservas_confirmadas": total_reservas,
        "reservas_percent": reservas_percent,           # ← con 3 decimales
        "cancelaciones": total_cancelaciones,
        "cancelaciones_percent": cancelaciones_percent  # ← con 3 decimales
    })

@app.route('/api/top_hoteles')
def api_top_hoteles():
    top_hoteles = OpinionesTuristicasDAO.obtener_top_hoteles()
    return jsonify(top_hoteles)

@app.route('/api/top_servicios')
def api_top_servicios():
    top_servicios = OpinionesTuristicasDAO.obtener_top_servicios()
    return jsonify(top_servicios)

@app.route('/api/top_rutas')
def api_top_rutas():
    top_rutas = OpinionesTuristicasDAO.obtener_top_rutas()
    return jsonify(top_rutas)

if __name__ == '__main__':
    # Escucha en todas las IPs (0.0.0.0) y puerto 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
