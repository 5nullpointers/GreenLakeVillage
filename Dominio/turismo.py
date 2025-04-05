from flask import Blueprint, render_template, jsonify, abort
from bson.objectid import ObjectId
from Persistencia.AgenteBD import MongoDBAgent
from Persistencia.DAOS.OpinionesTuristicasDAO import OpinionesTuristicasDAO

# Crear el blueprint para la sección de turismo
turismo_bp = Blueprint('turismo', __name__)

# Instanciar el agente de MongoDB
mongo_agent = MongoDBAgent()

# ---------------------------------------------------------------------
# GET /api/hoteles
# Retorna un JSON con todos los hoteles guardados en MongoDB.
# ---------------------------------------------------------------------
@turismo_bp.route('/api/hoteles', methods=['GET'])
def api_hoteles():
    hoteles = list(mongo_agent.db["hoteles"].find({}))
    for h in hoteles:
        h["_id"] = str(h["_id"])
    return jsonify(hoteles)

# ---------------------------------------------------------------------
# GET /api/ratings
# Retorna un JSON con la media de puntuación y el número de opiniones
# para cada hotel, con el nombre del servicio como clave.
# ---------------------------------------------------------------------
@turismo_bp.route('/api/ratings', methods=['GET'])
def api_ratings():
    agregados = OpinionesTuristicasDAO.obtener_agregados()
    ratings_dict = {
        entry["_id"]: {
            "media_puntuacion": entry["media_puntuacion"],
            "numero_comentarios": entry["numero_comentarios"]
        }
        for entry in agregados
    }
    return jsonify(ratings_dict)

# ---------------------------------------------------------------------
# GET /hoteles/<string:hotel_id>
# Muestra una página con más detalles de un hotel, incluyendo la sección
# de opiniones.
# ---------------------------------------------------------------------
@turismo_bp.route('/hoteles/<string:hotel_id>', methods=['GET'])
def hotel_detalle(hotel_id):
    try:
        obj_id = ObjectId(hotel_id)
    except Exception:
        return abort(400, description="ID inválido")
    
    hotel = mongo_agent.db["hoteles"].find_one({"_id": obj_id})
    if not hotel:
        return abort(404, description="Hotel no encontrado")
    hotel["_id"] = str(hotel["_id"])

    # Obtener opiniones y la media de la puntuación mediante el DAO
    opiniones, avg_rating = OpinionesTuristicasDAO.obtener_opiniones_y_media(hotel["nombre"])
    return render_template('hotel_detalles.html', hotel=hotel, opiniones=opiniones, avg_rating=avg_rating)

# ---------------------------------------------------------------------
# GET /api/rutas
# Retorna un JSON con todas las rutas turísticas guardadas en MongoDB.
# ---------------------------------------------------------------------
@turismo_bp.route('/api/rutas', methods=['GET'])
def api_rutas():
    rutas = list(mongo_agent.db["rutas_turisticas"].find({}))
    for r in rutas:
        r["_id"] = str(r["_id"])
    return jsonify(rutas)

# ---------------------------------------------------------------------
# GET /api/restaurantes
# Retorna un JSON con todos los restaurantes guardados en MongoDB.
# ---------------------------------------------------------------------
@turismo_bp.route('/api/restaurantes', methods=['GET'])
def api_restaurantes():
    restaurantes = list(mongo_agent.db["restaurantes"].find({}))
    for r in restaurantes:
        r["_id"] = str(r["_id"])
    return jsonify(restaurantes)