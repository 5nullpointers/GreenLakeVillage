import sys
import signal
import os
import pandas as pd
import numpy as np
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
load_dotenv(dotenv_path)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import openai
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from Entidades.RutasTuristicas import RutasTuristicas
from bson.objectid import ObjectId
from datetime import datetime, date
from Entidades.OcupacionHotelera import OcupacionHotelera
from Entidades.OpinionesTuristicas import OpinionesTuristicas
from Entidades.Sostenibilidad import Sostenibilidad
from Entidades.UsoTransporte import UsoTransporte
from Persistencia.DAOS.OpinionesTuristicasDAO import OpinionesTuristicasDAO
from Persistencia.DAOS.UserDAO import UserDAO
from Persistencia.DAOS.ReservasDAO import ReservasDAO

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

@app.route('/reserva_confirmada')
def reserva_confirmada():
    return render_template("reserva_confirmada.html")

@app.route('/reservar/<hotel_id>')
def reservar_page(hotel_id):
    """Muestra el formulario de reserva para un hotel concreto."""
    hotel = mongo_agent.db["hoteles"].find_one({"_id": ObjectId(hotel_id)})
    if not hotel:
        return "Hotel no encontrado", 404

    hotel["_id"] = str(hotel["_id"])
    error_message = request.args.get("error", "")
    return render_template("reservar.html", hotel=hotel, error_message=error_message)

@app.route('/reservas', methods=['POST'])
def crear_reserva():
    """
    Procesa el formulario de reserva:
      hotel_id, startDate (YYYY-MM-DD), endDate (YYYY-MM-DD), numPersons (opcional).
    Validaciones:
      1) El usuario debe estar autenticado y tener rol "Tourist" (no ser "Anónimo").
      2) La fecha de fin debe ser posterior a la de inicio.
      3) La fecha de inicio no puede estar en el pasado.
      4) No debe haber solapamientos con reservas del mismo hotel.
    Inserta la reserva en la colección 'reservas' usando ReservasDAO.
    """
    # Verificar si el usuario está autenticado
    if 'user_id' not in session:
        return """
        <script>
            alert("Debes iniciar sesión para reservar.");
            window.history.back();
        </script>
        """
    
    user_name = session.get("user_name", None)
    from Persistencia.DAOS.UserDAO import UserDAO
    usuario = UserDAO.obtener_dato({"_id": ObjectId(session["user_id"])})
    if not user_name or user_name == "Anónimo" or usuario.get("type") != "Tourist":
        return """
        <script>
            alert("No se puede realizar la reserva si eres Anónimo o no tienes el rol de Tourist. Por favor, inicia sesión o regístrate.");
            window.history.back();
        </script>
        """
    
    # Obtener datos del formulario
    hotel_id = request.form.get("hotel_id")
    start_str = request.form.get("startDate")
    end_str = request.form.get("endDate")
    num_persons = request.form.get("numPersons", "0")

    if not hotel_id or not start_str or not end_str:
        return "Faltan campos obligatorios", 400

    hotel_info = mongo_agent.db["hoteles"].find_one({"_id": ObjectId(hotel_id)})
    if not hotel_info:
        return "Hotel no encontrado", 404

    try:
        start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
    except ValueError:
        error_msg = "Formato de fecha inválido."
        return redirect(url_for('reservar_page', hotel_id=hotel_id, error=error_msg))

    if end_date <= start_date:
        error_msg = "La fecha de fin debe ser posterior a la de inicio."
        return redirect(url_for('reservar_page', hotel_id=hotel_id, error=error_msg))

    hoy = date.today()
    if start_date < hoy:
        error_msg = "No puedes reservar en una fecha pasada."
        return redirect(url_for('reservar_page', hotel_id=hotel_id, error=error_msg))

    reservas_cursor = ReservasDAO.obtener_reservas_por_hotel(hotel_id)
    for r in reservas_cursor:
        try:
            r_start = datetime.strptime(r["fecha_inicio"], "%Y-%m-%d").date()
            r_end = datetime.strptime(r["fecha_fin"], "%Y-%m-%d").date()
        except (KeyError, ValueError):
            continue
        if (start_date < r_end) and (end_date > r_start):
            error_msg = "El hotel ya está reservado en ese rango de fechas."
            return redirect(url_for('reservar_page', hotel_id=hotel_id, error=error_msg))

    nombre_hotel = hotel_info.get("nombre", "Desconocido")
    reserva_doc = {
        "hotelId": hotel_id,
        "nombre_hotel": nombre_hotel,
        "fecha_inicio": start_str,
        "fecha_fin": end_str,
        "numero_personas": int(num_persons) if num_persons.isdigit() else 0,
        "nombre_usuario": user_name,
        "fecha_reserva": datetime.utcnow()
    }
    ReservasDAO.insertar_reserva(reserva_doc)

    mongo_agent.db["hoteles"].update_one(
        {"_id": ObjectId(hotel_id)},
        {"$inc": {"reservas_count": 1}}
    )

    flash("Reserva creada satisfactoriamente.")
    return redirect(url_for('reserva_confirmada'))

@app.route('/login')
def login_page():
    # Ahora la ruta '/login' redirige a loginRegister.html
    return render_template('loginRegister.html')

@app.route('/Propietarios')
def Propietarios():
    return render_template('BusinessOwner.html')

@app.route('/Propietarios/ReservasHoteles')
def ver_reservas_hoteles():
    return render_template("ReservasBusinessOwner.html")

@app.route('/api/propietarios/reservas')
def api_reservas_propietario():
    user_name = session.get("user_name")

    # Obtener lista de propiedades del usuario
    usuario = mongo_agent.db["usuarios"].find_one({"name": user_name})
    if not usuario or "properties" not in usuario:
        return jsonify([])

    nombres_hoteles = usuario["properties"]
    
    # Para depuración, descomenta la siguiente línea para devolver todas las reservas
    # reservas = list(mongo_agent.db["reservas"].find({}))
    
    reservas = list(mongo_agent.db["reservas"].find({
        "nombre_hotel": {"$in": nombres_hoteles}
    }))
    for r in reservas:
        r["_id"] = str(r["_id"])
    return jsonify(reservas)

@app.route('/Propietarios/Previsiones')
def verPrevisiones():
    return render_template("PrevisionesBusinessOwner.html")

@app.route('/MapaAdmin')
def MapaAdmin():
    google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    return render_template('MapaAdmin.html', google_maps_api_key=google_maps_api_key)

@app.route('/MapaPropietarios')
def MapaPropietarios():
    google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    return render_template('MapaPropietarios.html', google_maps_api_key=google_maps_api_key)

@app.route('/admin/UsuariosAdmin')
def UsuariosAdmin():
    return render_template('UsuariosAdmin.html')

@app.route('/admin/ForoAdmin')
def ForoAdmin():
    return render_template('ForoAdmin.html')

@app.route('/api/admin/crear-tema', methods=['POST'])
def crear_tema():
    titulo = request.form.get("titulo")
    descripcion = request.form.get("descripcion")
    categoria = request.form.get("categoria")

    if not titulo or not descripcion:
        return jsonify({"error": "Falta el título o la descripción"}), 400
    
    nuevo_tema = {
        "titulo": titulo,
        "descripcion": descripcion,
        "autor": session.get("user_name", "Admin"),
        "fecha": datetime.utcnow(),
        "categoria": categoria,
        "estado": "activo"
    }
    result = mongo_agent.db["temas_forum"].insert_one(nuevo_tema)
    #Comprobar si se ha insertado correctamente
    if result.inserted_id:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False}), 500

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
    google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    return render_template('Admin.html', ingresosTotales=ingresos_totales, totalReservas=totalReservas, consumoTotal=consumo_total, google_maps_api_key=google_maps_api_key)

@app.route('/api/foro/temas')
def api_foro_temas():
    temas = list(mongo_agent.db["temas_forum"].find({}))
    for tema in temas:
        tema["_id"] = str(tema["_id"])
    return jsonify(temas)

@app.route('/api/foro/temas/<string:tema_id>/comentarios')
def api_foro_comentarios(tema_id):
    comentarios = list(mongo_agent.db["comentarios_forum"].find({"tema_id": tema_id}))
    for c in comentarios:
        c["_id"] = str(c["_id"])
    return jsonify(comentarios)

# Configuración para archivos
UPLOAD_FOLDER = os.path.join(STATIC_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/foro/comentar', methods=['POST'])
def api_foro_comentar():
    tema_id = request.form.get("tema_id")
    comentario_texto = request.form.get("comentario")
    # Obtener usuario desde la sesión
    autor = session.get("user_name", "Anónimo")
    imagen_url = None

    # Manejar la imagen si se envió
    if 'imagen' in request.files:
        file = request.files['imagen']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            # Construir la URL de la imagen
            imagen_url = '/static/uploads/' + filename

    comentario = {
        "tema_id": tema_id,
        "autor": autor,
        "comentario": comentario_texto,
        "imagen_url": imagen_url,
        "fecha": datetime.utcnow()
    }
    result = mongo_agent.db["comentarios_forum"].insert_one(comentario)
    if result.inserted_id:
        # Registrar el reto de comentario si aún no ha sido completado
        user_id = session.get("user_id")
        if user_id:
            try:
                usuario = mongo_agent.db["usuarios"].find_one({"_id": ObjectId(user_id)})
                if usuario:
                    # Aquí debes usar el id del reto correspondiente al "Reto de Comentario"
                    registrar_reto(usuario, "647a1ba13d5f1c4a9e8a1236")
            except Exception as e:
                print("Error registrando reto:", e)
        return jsonify({"success": True})
    else:
        return jsonify({"success": False}), 500



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

    if not email or not password:
        flash("Por favor, completa ambos campos.")
        return redirect(url_for('login_page'))

    usuario = UserDAO.obtener_dato({"email": email})
    if usuario:
        if usuario.get("blocked") == True:
            return redirect(url_for('UserBlock'))

        match usuario.get("type"):
            case "Tourist":
                if check_password_hash(usuario.get("pass"), password):
                    session['user_id'] = str(usuario["_id"])
                    session['user_name'] = usuario.get("name")
                    # Buscar todos los retos activos
                    retos = list(mongo_agent.db["retos"].find({"activo": True}))
                    retos_pendientes = []
                    # Obtener los retos ya completados por el usuario
                    retos_completados = usuario.get("retos_completados", [])
                    # Filtrar aquellos retos que no hayan sido notificados (popup_mostrado True)
                    for reto in retos:
                        reto_id = str(reto["_id"])
                        if not any(str(r["reto_id"]) == reto_id and r.get("popup_mostrado", False) for r in retos_completados):
                            retos_pendientes.append(reto)
                    
                    # Almacenar en la sesión la lista de retos pendientes para que el front-end los muestre
                    session['retos_pendientes'] = retos_pendientes
                    flash("Inicio de sesión exitoso!")
                    return redirect(url_for('map'))
                else:
                    flash("Contraseña incorrecta.")
                    return redirect(url_for('login_page'))
            case "Admin":
                if check_password_hash(usuario.get("pass"), password):
                    session['user_id'] = str(usuario["_id"])
                    session['user_name'] = usuario.get("name")
                    flash("Inicio de sesión exitoso!")
                    return redirect(url_for('admin'))
                else:
                    flash("Contraseña incorrecta.")
                    return redirect(url_for('login_page'))
            case "BusinessOwner":
                if check_password_hash(usuario.get("pass"), password):
                    session['user_id'] = str(usuario["_id"])
                    session['user_name'] = usuario.get("name")
                    flash("Inicio de sesión exitoso!")
                    return redirect(url_for('Propietarios'))
                else:
                    flash("Contraseña incorrecta.")
                    return redirect(url_for('login_page'))
            case _:
                flash("Tipo de usuario desconocido.")
                return redirect(url_for('login_page'))
    else:
        flash("Usuario no encontrado.")
        return redirect(url_for('login_page'))


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



@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    blocked = False

    if not name or not email or not password:
        flash("Todos los campos son obligatorios.")
        return redirect(url_for('login_page'))

    if UserDAO.obtener_dato({"email": email}):
        flash("El correo ya está registrado.")
        return redirect(url_for('login_page'))

    hashed_password = generate_password_hash(password)
    nuevo_usuario = {
        "name": name,
        "email": email,
        "pass": hashed_password,
        "type": "Tourist",
        "blocked": blocked,
        "preferencias": [],
        "retos_completados": [],
        "tokens": 0
    }

    UserDAO.insertar_dato(nuevo_usuario)

    usuario = UserDAO.obtener_dato({"email": email})
    if usuario:
        # Registrar el reto de registro para que no se muestre en futuras sesiones
        registrar_reto(usuario, "647a1b9f3d5f1c4a9e8a1234")
        # Almacenar el _id (como string) en la sesión
        session['user_id'] = str(usuario["_id"])
        session['user_name'] = usuario.get("name")
    else:
        flash("Error en el registro")
        return redirect(url_for('login_page'))

    flash("Registro exitoso. Ahora elige tus preferencias.")
    return redirect(url_for('preferences', user_email=email))



@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    # Obtener el correo del usuario desde la URL
    user_email = request.args.get('user_email')
    usuario = UserDAO.obtener_dato({"email": user_email})

    if request.method == 'POST':
        # Recibir las preferencias seleccionadas desde el formulario
        preferences = request.form.getlist('preferences')

        # Actualizar las preferencias del usuario en la base de datos
        UserDAO.actualizar_dato(
            {"email": user_email},
            {"preferencias": preferences}
        )

        flash("Tus preferencias se han guardado correctamente.")
        return redirect(url_for('map'))  # Redirigir al mapa u otra página

    return render_template('Preferences.html', user=usuario)


@app.route('/save-preferences', methods=['POST'])
def save_preferences():
    data = request.json
    # Obtenemos el _id del usuario (almacenado en la sesión)
    user_id = session.get('user_id')
    preferences = data.get('preferencias')

    if not user_id or not preferences:
        return jsonify({"error": "Email o preferencias no proporcionadas"}), 400

    print(f"User ID: {user_id}, Preferencias: {preferences}")  # Verificar los datos recibidos

    try:
        # Buscar al usuario en la base de datos utilizando el _id
        from bson import ObjectId
        user = UserDAO.obtener_dato({"_id": ObjectId(user_id)})

        # Verificar si el usuario fue encontrado
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 400

        # Actualizar las preferencias del usuario
        result = UserDAO.actualizar_dato(
            {"_id": ObjectId(user_id)},
            {"preferencias": preferences}
        )

        print(f"Resultado de la actualización: {result.modified_count} documentos modificados")

        if result.modified_count > 0:
            return jsonify({"success": True, "redirect": url_for('map')})
        else:
            return jsonify({"error": "No se pudo actualizar las preferencias"}), 500
    except Exception as e:
        print(f"Error al guardar preferencias: {str(e)}")
        return jsonify({"error": str(e)}), 500


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

@app.route('/api/ratings_Propietarios')
def api_ratings_Propietarios():
    from bson import ObjectId
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    business_owner = UserDAO.obtener_dato({"_id": ObjectId(user_id)})
    if not business_owner or business_owner.get("type") != "BusinessOwner":
        return jsonify({"error": "El usuario no es un Propietario"}), 403

    user_properties = business_owner.get("properties", [])
    agregados = OpinionesTuristicasDAO.obtener_agregados()

    # Filtrar los resultados de 'agregados' solo por propiedades del usuario
    ratings_dict = {}
    for entry in agregados:
        if entry["_id"] in user_properties:
            ratings_dict[entry["_id"]] = {
                "media_puntuacion": entry["media_puntuacion"],
                "numero_comentarios": entry["numero_comentarios"]
            }
    return jsonify(ratings_dict)

from bson import ObjectId
from flask import render_template, abort
from Entidades.asistenteIA import obtener_respuesta

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

<<<<<<< HEAD
from bson import ObjectId

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



=======
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
>>>>>>> Admin-Interfaz

@app.route('/api/estadisticas_ocupacion')
def api_estadisticas_ocupacion():
    ocupaciones = OcupacionHoteleraDAO.obtener_todos()
    if not ocupaciones:
        return jsonify({
            "tasa_ocupacion_users": 0,
            "tasa_ocupacion_percent": 0,
            "reservas_confirmadas": 0,
            "reservas_percent": 0,
            "cancelaciones": 0,
            "cancelaciones_percent": 0
        })

    total_reservas = sum(o["reservas_confirmadas"] for o in ocupaciones)
    total_cancelaciones = sum(o["cancelaciones"] for o in ocupaciones)
    total_usuarios = total_reservas + total_cancelaciones

    total_tasa = sum(o["tasa_ocupacion"] for o in ocupaciones)
    promedio_tasa = round(total_tasa / len(ocupaciones), 3)

    if total_usuarios > 0:
        ocupacion_users = round((promedio_tasa / 100) * total_usuarios)
    else:
        ocupacion_users = 0

    if total_usuarios > 0:
        reservas_percent = round((total_reservas / total_usuarios) * 100, 3)
        cancelaciones_percent = round((total_cancelaciones / total_usuarios) * 100, 3)
    else:
        reservas_percent = 0
        cancelaciones_percent = 0

    # Aplica filtro short_number antes de devolver JSON
    from flask import current_app
    short = current_app.jinja_env.filters['short_number']  

    return jsonify({
        "tasa_ocupacion_users": short(ocupacion_users),
        "tasa_ocupacion_percent": promedio_tasa,  
        "reservas_confirmadas": short(total_reservas),
        "reservas_percent": reservas_percent,
        "cancelaciones": short(total_cancelaciones),
        "cancelaciones_percent": cancelaciones_percent
    })

<<<<<<< HEAD
@app.route('/api/estadisticas_ocupacion_Propietarios')
def api_estadisticas_ocupacion_Propietarios():
    # Nuevo: Obtener el usuario logueado y sus propiedades
    from Persistencia.DAOS.UserDAO import UserDAO
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Usuario no autenticado."}), 401
    business_owner = UserDAO.obtener_dato({"_id": ObjectId(user_id)})
    if not business_owner or business_owner.get("type") != "BusinessOwner":
        return jsonify({"error": "Acceso no autorizado."}), 403
    user_properties = business_owner.get("properties", [])
    
    # Obtener datos de ocupación y filtrar por propiedades del usuario
    all_ocupaciones = OcupacionHoteleraDAO.obtener_todos()
    ocupaciones = [o for o in all_ocupaciones if o.get("hotel_nombre") in user_properties]
    
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
    

    total_reservas = sum(o["reservas_confirmadas"] for o in ocupaciones)
    total_cancelaciones = sum(o["cancelaciones"] for o in ocupaciones)
    total_usuarios = total_reservas + total_cancelaciones

    # 2) Calcular promedios
    total_tasa = sum(o["tasa_ocupacion"] for o in ocupaciones)  # suma de % ocupacion
    promedio_tasa = round(total_tasa / len(ocupaciones), 3)     # promedio de % ocupacion

    if total_usuarios > 0:
        ocupacion_users = round((promedio_tasa / 100) * total_usuarios)
    else:
        ocupacion_users = 0


    if total_usuarios > 0:
        reservas_percent = round((total_reservas / total_usuarios) * 100, 3)
        cancelaciones_percent = round((total_cancelaciones / total_usuarios) * 100, 3)
    else:
        reservas_percent = 0
        cancelaciones_percent = 0

    return jsonify({
        "tasa_ocupacion_users": short(ocupacion_users),
        "tasa_ocupacion_percent": promedio_tasa,  
        "reservas_confirmadas": short(total_reservas),
        "reservas_percent": reservas_percent,
        "cancelaciones": short(total_cancelaciones),
        "cancelaciones_percent": cancelaciones_percent
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

@app.route('/api/uso_transporte')
def api_uso_transporte():

    datos = UsoTransporteDAO.obtener_todos()

    resumen = {}
    for dato in datos:
        tipo = dato.get("tipo_transporte", "Desconocido")
        num = dato.get("num_usuarios", 0)
        resumen[tipo] = resumen.get(tipo, 0) + num
    return jsonify(resumen)

@app.route('/Propietarios/PropiedadesUsuario', methods=['GET'])
def propiedades_usuario():
    """
    Muestra (o retorna en JSON) las propiedades de un usuario BusinessOwner.

    - Si es una petición normal (GET sin 'X-Requested-With'),
      se renderiza la plantilla 'PropiedadesUsuario.html' con Jinja2,
      mostrando las propiedades en un <ul>.

    - Si es una petición fetch/JS con 'X-Requested-With: XMLHttpRequest',
      se retorna JSON para que el front-end rellene la tabla <table id="propiedadesTable">.
    """
    user_id = session.get('user_id')
    if not user_id:
        # Si no hay usuario en sesión, respondemos según sea fetch o normal
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"error": "Usuario no autenticado."}), 401
        else:
            return "No hay usuario logueado. <a href='/login'>Ir a login</a>", 401

    # 1) Buscar al usuario con el UserDAO
    usuario = UserDAO.obtener_dato({"_id": ObjectId(user_id)})
    if not usuario:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"error": "Usuario no encontrado."}), 404
        else:
            return "Usuario no encontrado.", 404

    # 2) Extraer sus propiedades (array de strings)
    propiedades = usuario.get("properties", [])

    propiedades_info = []
    for propiedad in propiedades:
        # 3) Buscar datos de ocupación en "ocupacion_hotelera"
        ocupacion = OcupacionHoteleraDAO.obtener_por_nombre(propiedad) or {}
        # 4) Buscar opiniones en "opiniones_turisticas"
        opiniones = list(mongo_agent.db["opiniones_turisticas"].find({"hotel_nombre": propiedad}))
        # Calcular rating medio
        if opiniones:
            avg_rating = sum(op.get("puntuacion", 0) for op in opiniones) / len(opiniones)
        else:
            avg_rating = None

        tipo_servicio = OpinionesTuristicasDAO.obtener_tipo_servicio(propiedad)

        precio = ""

        # Obtener precio según el tipo
        if tipo_servicio == "Hotel":
            precio = ocupacion.get("precio_promedio_noche", "N/A")
        elif tipo_servicio == "Servicio":
            restaurante = mongo_agent.db["restaurantes"].find_one({"nombre": propiedad}) or {}
            precio = restaurante.get("precio_medio", "N/A")
        else:
            precio = "N/A"

        # 5) Construir la info de la propiedad
        propiedades_info.append({
            "nombre": propiedad,
            "tipo_servicio": tipo_servicio,
            "ocupacion": {
                "reservas_confirmadas": ocupacion.get("reservas_confirmadas", 0),
                "cancelaciones": ocupacion.get("cancelaciones", 0),
                "precio": precio
            },
            "opiniones": opiniones,
            "avg_rating": avg_rating
        })

    # 6) Si la petición es fetch/JS => devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(propiedades_info)

    # 7) Si no es fetch => renderizar la plantilla con Jinja2
    return render_template('PropiedadesUsuario.html', propiedades=propiedades_info)

@app.route('/api/billed_Propietarios')
def api_billed_Propietarios():
    from Persistencia.DAOS.UserDAO import UserDAO
    from Persistencia.DAOS.HotelesDAO import HotelesDAO
    from Persistencia.DAOS.OcupacionHoteleraDAO import OcupacionHoteleraDAO
    from bson import ObjectId

    user_id = session.get('user_id')
    if not user_id:
        return

    business_owner = UserDAO.obtener_dato({"_id": ObjectId(user_id)})
    if not business_owner or business_owner.get("type") != "BusinessOwner":
        return

    # Obtener propiedades del usuario
    user_properties = business_owner.get("properties", [])

    # Obtener precios de hoteles
    hoteles_data = HotelesDAO.obtener_precios()
    # Obtener reservas confirmadas
    ocupaciones_data = OcupacionHoteleraDAO.obtener_todos()

    # Construir un dict para precios
    precios_dict = {}
    for h in hoteles_data:
        nombre_hotel = h.get("nombre")
        precio_hotel = h.get("precio", 0)
        precios_dict[nombre_hotel] = precio_hotel

    # Construir un dict para reservas
    reservas_dict = {}
    for o in ocupaciones_data:
        nombre_occ = o.get("hotel_nombre")
        reservas = o.get("reservas_confirmadas", 0)
        reservas_dict[nombre_occ] = reservas_dict.get(nombre_occ, 0) + reservas

    # Calcular facturación
    facturacion = []
    for propiedad in user_properties:
        precio = precios_dict.get(propiedad, 0)
        reserv = reservas_dict.get(propiedad, 0)
        facturacion.append({
            "hotelName": propiedad,
            "total": precio * reserv
        })

    # Ordenar top 3
    facturacion.sort(key=lambda x: x["total"], reverse=True)
    top3 = facturacion[:3]

    return jsonify(top3)

from bson import ObjectId
import math  # Añade esta línea si no existe

@app.route('/api/latest_reviews_propietarios')
def api_latest_reviews_propietarios():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Usuario no autenticado."}), 401
    business_owner = UserDAO.obtener_dato({"_id": ObjectId(user_id)})
    if not business_owner or business_owner.get("type") != "BusinessOwner":
        return jsonify({"error": "Acceso no autorizado."}), 403
    user_properties = business_owner.get("properties", [])
    reseñas_cursor = mongo_agent.db["opiniones_turisticas"].find(
        {"nombre_servicio": {"$in": user_properties}}
    ).sort("fecha", -1).limit(3)
    reseñas = list(reseñas_cursor)
    for r in reseñas:
        r["_id"] = str(r["_id"])
        # Reemplazar cualquier valor NaN en el registro por None
        for key, value in r.items():
            if isinstance(value, float) and math.isnan(value):
                r[key] = None
    return jsonify(reseñas)

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

import pandas as pd
import numpy as np
from bson import ObjectId
from flask import jsonify, session

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

@app.route('/api/prediccionesOcupacion_Propietarios')
def api_predicciones_ocupacion_propietarios():
    """
    Devuelve las previsiones de ocupación, reservas, cancelaciones y precio
    solo para los hoteles/restaurantes del usuario BusinessOwner.
    
    Se asume que la colección 'ocupacion_hotelera' tiene:
        - hotel_nombre
        - fecha (datetime)
        - tasa_ocupacion (int/float)
        - reservas_confirmadas (int)
        - cancelaciones (int)
        - precio_promedio_noche (float)
    """
    try:
        # Verificar que el usuario está autenticado
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Usuario no autenticado"}), 401

        # Verificar que sea un BusinessOwner
        business_owner = mongo_agent.db["usuarios"].find_one({"_id": ObjectId(user_id)})
        if not business_owner or business_owner.get("type") != "BusinessOwner":
            return jsonify({"error": "Acceso no autorizado"}), 403

        # Obtener propiedades (hoteles) del usuario
        user_properties = business_owner.get("properties", [])
        if not user_properties:
            return jsonify([])  # Sin propiedades, retorna lista vacía

        # Obtener datos históricos desde 'ocupacion_hotelera' solo de esas propiedades
        data_cursor = mongo_agent.db["ocupacion_hotelera"].find({
            "hotel_nombre": {"$in": user_properties}
        })
        data = list(data_cursor)
        if not data:
            return jsonify([])  # Sin datos para predecir

        # Convertir a DataFrame y asegurar fecha como datetime
        df = pd.DataFrame(data)
        df['fecha'] = pd.to_datetime(df['fecha'])

        forecast_horizon = 12 # Predecir para los próximos 3 meses
        predictions = []

        # Agrupar por hotel_nombre
        for hotel_name, group in df.groupby('hotel_nombre'):
            group = group.sort_values('fecha')  # Ordenar por fecha ascendente
            last_date = group['fecha'].max()

            # Series de datos
            tasa_series = group['tasa_ocupacion'].tolist()
            reservas_series = group['reservas_confirmadas'].tolist()
            cancelaciones_series = group['cancelaciones'].tolist()
            precio_series = group['precio_promedio_noche'].tolist()

            # Predecir cada métrica
            pred_tasa = forecast_series(tasa_series, forecast_horizon)
            pred_reservas = forecast_series(reservas_series, forecast_horizon)
            pred_cancelaciones = forecast_series(cancelaciones_series, forecast_horizon)
            pred_precio = forecast_series(precio_series, forecast_horizon)

            # Construir predicciones para cada mes futuro
            for i in range(forecast_horizon):
                future_date = last_date + pd.DateOffset(months=i+1)
                predictions.append({
                    "mes": future_date.strftime("%Y-%m"),
                    "hotel_nombre": hotel_name,
                    "tasa_ocupacion": round(pred_tasa[i], 2),
                    "reservas_confirmadas": int(round(pred_reservas[i])),
                    "cancelaciones": int(round(pred_cancelaciones[i])),
                    "precio_promedio_noche": round(pred_precio[i], 2)
                })

        return jsonify(predictions)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

=======
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

@app.route('/api/uso_transporte')
def api_uso_transporte():

    datos = UsoTransporteDAO.obtener_todos()

    resumen = {}
    for dato in datos:
        tipo = dato.get("tipo_transporte", "Desconocido")
        num = dato.get("num_usuarios", 0)
        resumen[tipo] = resumen.get(tipo, 0) + num
    return jsonify(resumen)
>>>>>>> Admin-Interfaz

@app.route('/api/estadisticas_ocupacion_Propietarios')
def api_estadisticas_ocupacion_Propietarios():
    # Nuevo: Obtener el usuario logueado y sus propiedades
    from Persistencia.DAOS.UserDAO import UserDAO
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Usuario no autenticado."}), 401
    business_owner = UserDAO.obtener_dato({"_id": ObjectId(user_id)})
    if not business_owner or business_owner.get("type") != "BusinessOwner":
        return jsonify({"error": "Acceso no autorizado."}), 403
    user_properties = business_owner.get("properties", [])
    
    # Obtener datos de ocupación y filtrar por propiedades del usuario
    all_ocupaciones = OcupacionHoteleraDAO.obtener_todos()
    ocupaciones = [o for o in all_ocupaciones if o.get("hotel_nombre") in user_properties]
    
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
    if total_usuarios > 0:
        ocupacion_users = round((promedio_tasa / 100) * total_usuarios)
    else:
        ocupacion_users = 0

    # 4) Calcular porcentajes de reservas y cancelaciones sobre el total
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

@app.route('/Propietarios/PropiedadesUsuario', methods=['GET'])
def propiedades_usuario():
    """
    Muestra (o retorna en JSON) las propiedades de un usuario BusinessOwner.

    - Si es una petición normal (GET sin 'X-Requested-With'),
      se renderiza la plantilla 'PropiedadesUsuario.html' con Jinja2,
      mostrando las propiedades en un <ul>.

    - Si es una petición fetch/JS con 'X-Requested-With: XMLHttpRequest',
      se retorna JSON para que el front-end rellene la tabla <table id="propiedadesTable">.
    """
    user_id = session.get('user_id')
    if not user_id:
        # Si no hay usuario en sesión, respondemos según sea fetch o normal
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"error": "Usuario no autenticado."}), 401
        else:
            return "No hay usuario logueado. <a href='/login'>Ir a login</a>", 401

    # 1) Buscar al usuario con el UserDAO
    usuario = UserDAO.obtener_dato({"_id": ObjectId(user_id)})
    if not usuario:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"error": "Usuario no encontrado."}), 404
        else:
            return "Usuario no encontrado.", 404

    # 2) Extraer sus propiedades (array de strings)
    propiedades = usuario.get("properties", [])

    propiedades_info = []
    for propiedad in propiedades:
        # 3) Buscar datos de ocupación en "ocupacion_hotelera"
        ocupacion = OcupacionHoteleraDAO.obtener_por_nombre(propiedad) or {}
        # 4) Buscar opiniones en "opiniones_turisticas"
        opiniones = list(mongo_agent.db["opiniones_turisticas"].find({"hotel_nombre": propiedad}))
        # Calcular rating medio
        if opiniones:
            avg_rating = sum(op.get("puntuacion", 0) for op in opiniones) / len(opiniones)
        else:
            avg_rating = None

        tipo_servicio = OpinionesTuristicasDAO.obtener_tipo_servicio(propiedad)

        precio = ""

        # Obtener precio según el tipo
        if tipo_servicio == "Hotel":
            precio = ocupacion.get("precio_promedio_noche", "N/A")
        elif tipo_servicio == "Servicio":
            restaurante = mongo_agent.db["restaurantes"].find_one({"nombre": propiedad}) or {}
            precio = restaurante.get("precio_medio", "N/A")
        else:
            precio = "N/A"

        # 5) Construir la info de la propiedad
        propiedades_info.append({
            "nombre": propiedad,
            "tipo_servicio": tipo_servicio,
            "ocupacion": {
                "reservas_confirmadas": ocupacion.get("reservas_confirmadas", 0),
                "cancelaciones": ocupacion.get("cancelaciones", 0),
                "precio": precio
            },
            "opiniones": opiniones,
            "avg_rating": avg_rating
        })

    # 6) Si la petición es fetch/JS => devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(propiedades_info)

    # 7) Si no es fetch => renderizar la plantilla con Jinja2
    return render_template('PropiedadesUsuario.html', propiedades=propiedades_info)

@app.route('/api/billed_Propietarios')
def api_billed_Propietarios():
    from Persistencia.DAOS.UserDAO import UserDAO
    from Persistencia.DAOS.HotelesDAO import HotelesDAO
    from Persistencia.DAOS.OcupacionHoteleraDAO import OcupacionHoteleraDAO
    from bson import ObjectId

    user_id = session.get('user_id')
    if not user_id:
        return

    business_owner = UserDAO.obtener_dato({"_id": ObjectId(user_id)})
    if not business_owner or business_owner.get("type") != "BusinessOwner":
        return

    # Obtener propiedades del usuario
    user_properties = business_owner.get("properties", [])

    # Obtener precios de hoteles
    hoteles_data = HotelesDAO.obtener_precios()
    # Obtener reservas confirmadas
    ocupaciones_data = OcupacionHoteleraDAO.obtener_todos()

    # Construir un dict para precios
    precios_dict = {}
    for h in hoteles_data:
        nombre_hotel = h.get("nombre")
        precio_hotel = h.get("precio", 0)
        precios_dict[nombre_hotel] = precio_hotel

    # Construir un dict para reservas
    reservas_dict = {}
    for o in ocupaciones_data:
        nombre_occ = o.get("hotel_nombre")
        reservas = o.get("reservas_confirmadas", 0)
        reservas_dict[nombre_occ] = reservas_dict.get(nombre_occ, 0) + reservas

    # Calcular facturación
    facturacion = []
    for propiedad in user_properties:
        precio = precios_dict.get(propiedad, 0)
        reserv = reservas_dict.get(propiedad, 0)
        facturacion.append({
            "hotelName": propiedad,
            "total": precio * reserv
        })

    # Ordenar top 3
    facturacion.sort(key=lambda x: x["total"], reverse=True)
    top3 = facturacion[:3]

    return jsonify(top3)

from bson import ObjectId
import math  # Añade esta línea si no existe

@app.route('/api/latest_reviews_propietarios')
def api_latest_reviews_propietarios():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Usuario no autenticado."}), 401
    business_owner = UserDAO.obtener_dato({"_id": ObjectId(user_id)})
    if not business_owner or business_owner.get("type") != "BusinessOwner":
        return jsonify({"error": "Acceso no autorizado."}), 403
    user_properties = business_owner.get("properties", [])
    reseñas_cursor = mongo_agent.db["opiniones_turisticas"].find(
        {"nombre_servicio": {"$in": user_properties}}
    ).sort("fecha", -1).limit(3)
    reseñas = list(reseñas_cursor)
    for r in reseñas:
        r["_id"] = str(r["_id"])
        # Reemplazar cualquier valor NaN en el registro por None
        for key, value in r.items():
            if isinstance(value, float) and math.isnan(value):
                r[key] = None
    return jsonify(reseñas)

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

import pandas as pd
import numpy as np
from bson import ObjectId
from flask import jsonify, session

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

@app.route('/api/prediccionesOcupacion_Propietarios')
def api_predicciones_ocupacion_propietarios():
    """
    Devuelve las previsiones de ocupación, reservas, cancelaciones y precio
    solo para los hoteles/restaurantes del usuario BusinessOwner.
    
    Se asume que la colección 'ocupacion_hotelera' tiene:
        - hotel_nombre
        - fecha (datetime)
        - tasa_ocupacion (int/float)
        - reservas_confirmadas (int)
        - cancelaciones (int)
        - precio_promedio_noche (float)
    """
    try:
        # Verificar que el usuario está autenticado
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"error": "Usuario no autenticado"}), 401

        # Verificar que sea un BusinessOwner
        business_owner = mongo_agent.db["usuarios"].find_one({"_id": ObjectId(user_id)})
        if not business_owner or business_owner.get("type") != "BusinessOwner":
            return jsonify({"error": "Acceso no autorizado"}), 403

        # Obtener propiedades (hoteles) del usuario
        user_properties = business_owner.get("properties", [])
        if not user_properties:
            return jsonify([])  # Sin propiedades, retorna lista vacía

        # Obtener datos históricos desde 'ocupacion_hotelera' solo de esas propiedades
        data_cursor = mongo_agent.db["ocupacion_hotelera"].find({
            "hotel_nombre": {"$in": user_properties}
        })
        data = list(data_cursor)
        if not data:
            return jsonify([])  # Sin datos para predecir

        # Convertir a DataFrame y asegurar fecha como datetime
        df = pd.DataFrame(data)
        df['fecha'] = pd.to_datetime(df['fecha'])

        forecast_horizon = 12 # Predecir para los próximos 3 meses
        predictions = []

        # Agrupar por hotel_nombre
        for hotel_name, group in df.groupby('hotel_nombre'):
            group = group.sort_values('fecha')  # Ordenar por fecha ascendente
            last_date = group['fecha'].max()

            # Series de datos
            tasa_series = group['tasa_ocupacion'].tolist()
            reservas_series = group['reservas_confirmadas'].tolist()
            cancelaciones_series = group['cancelaciones'].tolist()
            precio_series = group['precio_promedio_noche'].tolist()

            # Predecir cada métrica
            pred_tasa = forecast_series(tasa_series, forecast_horizon)
            pred_reservas = forecast_series(reservas_series, forecast_horizon)
            pred_cancelaciones = forecast_series(cancelaciones_series, forecast_horizon)
            pred_precio = forecast_series(precio_series, forecast_horizon)

            # Construir predicciones para cada mes futuro
            for i in range(forecast_horizon):
                future_date = last_date + pd.DateOffset(months=i+1)
                predictions.append({
                    "mes": future_date.strftime("%Y-%m"),
                    "hotel_nombre": hotel_name,
                    "tasa_ocupacion": round(pred_tasa[i], 2),
                    "reservas_confirmadas": int(round(pred_reservas[i])),
                    "cancelaciones": int(round(pred_cancelaciones[i])),
                    "precio_promedio_noche": round(pred_precio[i], 2)
                })

        return jsonify(predictions)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Escucha en todas las IPs (0.0.0.0) y puerto 5000
    app.run(host='0.0.0.0', port=5000, debug=True)