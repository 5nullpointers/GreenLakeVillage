from flask import Blueprint, jsonify, render_template, request, session
from Persistencia.AgenteBD import MongoDBAgent
from Persistencia.DAOS.UserDAO import UserDAO
from Persistencia.DAOS.OcupacionHoteleraDAO import OcupacionHoteleraDAO
from Persistencia.DAOS.OpinionesTuristicasDAO import OpinionesTuristicasDAO
from Persistencia.DAOS.HotelesDAO import HotelesDAO
from bson import ObjectId

import os
import pandas as pd
import math
import numpy as np

mongo_agent = MongoDBAgent()
propietarios_bp = Blueprint('propietarios', __name__)

# -------------------------------
# Función auxiliar para predecir con regresión lineal simple
# -------------------------------
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

# -------------------------------
# GET / - Página principal de propietarios
# -------------------------------
@propietarios_bp.route('/')
def Propietarios():
    return render_template('BusinessOwner.html')

# -------------------------------
# GET /Previsiones - Página de previsiones para BusinessOwner
# -------------------------------
@propietarios_bp.route('/Previsiones')
def verPrevisiones():
    return render_template("PrevisionesBusinessOwner.html")

# -------------------------------
# GET /MapaPropietarios - Mapa para propietarios
# -------------------------------
@propietarios_bp.route('/MapaPropietarios')
def MapaPropietarios():
    google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    return render_template('MapaPropietarios.html', google_maps_api_key=google_maps_api_key)

# -------------------------------
# GET /ReservasHoteles - Página de reservas de hoteles
# -------------------------------
@propietarios_bp.route('/ReservasHoteles')
def ver_reservas_hoteles():
    return render_template("ReservasBusinessOwner.html")

# -------------------------------
# GET /PropiedadesUsuario - Muestra propiedades del usuario BusinessOwner
# -------------------------------
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

# -------------------------------
# GET /api/propietarios/reservas - API de reservas para propietarios
# -------------------------------
@propietarios_bp.route('/api/propietarios/reservas')
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

# -------------------------------
# GET /api/ratings_Propietarios - API de ratings para propietarios
# -------------------------------
@propietarios_bp.route('/api/ratings_Propietarios')
def api_ratings_Propietarios():
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

# -------------------------------
# GET /api/billed_Propietarios - API de facturación para propietarios
# -------------------------------
@propietarios_bp.route('/api/billed_Propietarios')
def api_billed_Propietarios():

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

# -------------------------------
# GET /api/prediccionesOcupacion_Propietarios - API de predicciones de ocupación para propietarios
# -------------------------------
@propietarios_bp.route('/api/prediccionesOcupacion_Propietarios')
def api_predicciones_ocupacion_propietarios():
    from Dominio.prueba1 import forecast_series  # importación local para romper la circularidad
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

# -------------------------------
# GET /api/latest_reviews_propietarios - API de últimas reseñas para propietarios
# -------------------------------
@propietarios_bp.route('/api/latest_reviews_propietarios')
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

# -------------------------------
# API /estadisticas_ocupacion_Propietarios - API de estadísticas de ocupación para propietarios
# -------------------------------
@propietarios_bp.route('/api/estadisticas_ocupacion_Propietarios')
def api_estadisticas_ocupacion_Propietarios():
    # Nuevo: Obtener el usuario logueado y sus propiedades
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
        "tasa_ocupacion_users": ocupacion_users,
        "tasa_ocupacion_percent": promedio_tasa,  
        "reservas_confirmadas": total_reservas,
        "reservas_percent": reservas_percent,
        "cancelaciones": total_cancelaciones,
        "cancelaciones_percent": cancelaciones_percent
    })