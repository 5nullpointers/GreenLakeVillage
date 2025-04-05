from flask import Blueprint, jsonify, render_template, request, current_app
from Persistencia.AgenteBD import MongoDBAgent
from Persistencia.DAOS.UserDAO import UserDAO
from Persistencia.DAOS.OcupacionHoteleraDAO import OcupacionHoteleraDAO
from Persistencia.DAOS.HotelesDAO import HotelesDAO
from Persistencia.DAOS.SostenibilidadDAO import SostenibilidadDAO
from Persistencia.DAOS.OpinionesTuristicasDAO import OpinionesTuristicasDAO
from Persistencia.DAOS.UsoTransporteDAO import UsoTransporteDAO
from bson import ObjectId
import os

mongo_agent = MongoDBAgent()
admin_bp = Blueprint('admin', __name__)

# -------------------------------
# GET / - Panel de administración
# -------------------------------
@admin_bp.route('/')
def admin():
    consumo_total = SostenibilidadDAO.obtener_Consumo()
    totalReservas = OcupacionHoteleraDAO.UsuariosTotales()
    hoteles = HotelesDAO.obtener_precios()
    ocupaciones = list(mongo_agent.db["ocupacion_hotelera"].find({}, {"hotel_nombre": 1, "reservas_confirmadas": 1}))
    
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
        ingresos_totales += ingreso
    google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    return render_template('Admin.html', ingresosTotales=ingresos_totales, totalReservas=totalReservas, consumoTotal=consumo_total, google_maps_api_key=google_maps_api_key)

# -------------------------------
# GET /MapaAdmin - Mapa de administración
# -------------------------------
@admin_bp.route('/MapaAdmin')
def MapaAdmin():
    google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    return render_template('MapaAdmin.html', google_maps_api_key=google_maps_api_key)

# -------------------------------
# GET /UsuariosAdmin - Página de gestión de usuarios
# -------------------------------
@admin_bp.route('/UsuariosAdmin')
def UsuariosAdmin():
    return render_template('UsuariosAdmin.html')

# -------------------------------
# GET /ForoAdmin - Página del foro de administración
# -------------------------------
@admin_bp.route('/ForoAdmin')
def ForoAdmin():
    return render_template('ForoAdmin.html')

# -------------------------------
# POST /blockUser - Bloquear usuario
# -------------------------------
@admin_bp.route('/blockUser', methods=['POST'])
def block_user():
    data = request.get_json()
    user_id = data.get("id")
    if not user_id:
        return jsonify({"error": "ID de usuario no proporcionado."}), 400
    try:
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
    
# -------------------------------
# POST /unblockUser - Desbloquear usuario
# -------------------------------
@admin_bp.route('/unblockUser', methods=['POST'])
def unblock_user():
    data = request.get_json()
    user_id = data.get("id")
    if not user_id:
        return jsonify({"error": "ID de usuario no proporcionado."}), 400
    try:
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
    
# -------------------------------
# POST /deleteUser - Eliminar usuario
# -------------------------------
@admin_bp.route('/deleteUser', methods=['POST'])
def delete_user():
    data = request.get_json()
    user_id = data.get("id")
    if not user_id:
        return jsonify({"error": "ID de usuario no proporcionado."}), 400
    try:
        result = UserDAO.borrar_dato({"_id": ObjectId(user_id)})
        if result.deleted_count > 0:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "No se pudo eliminar el usuario."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------
# POST /editUser - Editar usuario
# -------------------------------
@admin_bp.route('/editUser', methods=['POST'])
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

# -------------------------------
# API /api/estadisticas_ocupacion - Obtener estadísticas de ocupación
# -------------------------------
@admin_bp.route('/api/estadisticas_ocupacion')
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
    short = current_app.jinja_env.filters['short_number']  

    return jsonify({
        "tasa_ocupacion_users": short(ocupacion_users),
        "tasa_ocupacion_percent": promedio_tasa,  
        "reservas_confirmadas": short(total_reservas),
        "reservas_percent": reservas_percent,
        "cancelaciones": short(total_cancelaciones),
        "cancelaciones_percent": cancelaciones_percent
    })

# -------------------------------
# API /api/top_hoteles - Obtener los 3 mejores hoteles
# -------------------------------
@admin_bp.route('/api/top_hoteles')
def api_top_hoteles():
    top_hoteles = OpinionesTuristicasDAO.obtener_top_hoteles()
    return jsonify(top_hoteles)

# -------------------------------
# API /api/top_servicios - Obtener los 3 mejores servicios
# -------------------------------
@admin_bp.route('/api/top_servicios')
def api_top_servicios():
    top_servicios = OpinionesTuristicasDAO.obtener_top_servicios()
    return jsonify(top_servicios)

# -------------------------------
# API /api/top_rutas - Obtener las 3 mejores rutas
# -------------------------------
@admin_bp.route('/api/top_rutas')
def api_top_rutas():
    top_rutas = OpinionesTuristicasDAO.obtener_top_rutas()
    return jsonify(top_rutas)

# -------------------------------
# API /api/uso_transporte - Obtener estadísticas de uso de transporte
# -------------------------------
@admin_bp.route('/api/uso_transporte')
def api_uso_transporte():

    datos = UsoTransporteDAO.obtener_todos()

    resumen = {}
    for dato in datos:
        tipo = dato.get("tipo_transporte", "Desconocido")
        num = dato.get("num_usuarios", 0)
        resumen[tipo] = resumen.get(tipo, 0) + num
    return jsonify(resumen)