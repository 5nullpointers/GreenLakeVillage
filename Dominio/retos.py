from datetime import datetime
from flask import Blueprint, request, jsonify, session
from bson.objectid import ObjectId
from Persistencia.AgenteBD import MongoDBAgent

# Crear el blueprint para retos
retos_bp = Blueprint('retos', __name__)

# Instanciar el agente de MongoDB
mongo_agent = MongoDBAgent()

# ---------------------------------------------------------------------
# POST /api/retos/marcar_notificado
# Actualiza un reto para indicar que ya se mostró la notificación.
# ---------------------------------------------------------------------
@retos_bp.route('/marcar_notificado', methods=['POST'])
def marcar_reto_notificado():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Usuario no autenticado"}), 401

    reto_id = request.json.get("reto_id")
    if not reto_id:
        return jsonify({"error": "Reto id no proporcionado"}), 400

    try:
        result = mongo_agent.db["usuarios"].update_one(
            {"_id": ObjectId(user_id), "retos_completados.reto_id": reto_id},
            {"$set": {"retos_completados.$.popup_mostrado": True}}
        )
        if result.modified_count > 0:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "No se pudo actualizar el reto."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------------------
# GET /api/retos/pendientes
# Retorna la lista de retos pendientes que aún no han sido notificados.
# ---------------------------------------------------------------------
@retos_bp.route('/pendientes', methods=['GET'])
def retos_pendientes():
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
    # Se consideran los retos que no han sido notificados (popup_mostrado: False)
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

# ---------------------------------------------------------------------
# Función auxiliar: registrar_reto
# Registra un reto en el usuario, si no ha sido registrado previamente.
# ---------------------------------------------------------------------
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