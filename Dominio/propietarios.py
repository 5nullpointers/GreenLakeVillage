from flask import Blueprint, jsonify, render_template, request, session
from Persistencia.AgenteBD import MongoDBAgent
from Persistencia.DAOS.UserDAO import UserDAO
from Persistencia.DAOS.OcupacionHoteleraDAO import OcupacionHoteleraDAO
from Persistencia.DAOS.OpinionesTuristicasDAO import OpinionesTuristicasDAO
from bson import ObjectId

import os

mongo_agent = MongoDBAgent()
propietarios_bp = Blueprint('propietarios', __name__)

@propietarios_bp.route('/ruta1')
def ruta1():
    return jsonify({"message": "Ruta 1 en propietarios"})

@propietarios_bp.route('/')
def Propietarios():
    return render_template('BusinessOwner.html')

@propietarios_bp.route('/Previsiones')
def verPrevisiones():
    return render_template("PrevisionesBusinessOwner.html")

@propietarios_bp.route('/MapaPropietarios')
def MapaPropietarios():
    google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    return render_template('MapaPropietarios.html', google_maps_api_key=google_maps_api_key)

@propietarios_bp.route('/ReservasHoteles')
def ver_reservas_hoteles():
    return render_template("ReservasBusinessOwner.html")

@propietarios_bp.route('/PropiedadesUsuario', methods=['GET'])
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