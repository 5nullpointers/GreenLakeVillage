from flask import Blueprint, render_template, request, jsonify, session
from bson.objectid import ObjectId
from Persistencia.AgenteBD import MongoDBAgent
from Entidades.asistenteIA import obtener_respuesta

# Crear el blueprint para las rutas generales
general_bp = Blueprint('general', __name__)

mongo_agent = MongoDBAgent()

# ---------------------------------------------------------------------
# GET /contacto
# Muestra la página de contacto.
# ---------------------------------------------------------------------
@general_bp.route('/contacto', methods=['GET'])
def contacto():
    return render_template('contacto.html')

# ---------------------------------------------------------------------
# GET /descubrir
# Muestra la página de descubrir.
# ---------------------------------------------------------------------
@general_bp.route('/descubrir', methods=['GET'])
def descubrir():
    return render_template('descubrir.html')

# ---------------------------------------------------------------------
# POST /chat
# Procesa los mensajes de chat y retorna la respuesta generada.
# ---------------------------------------------------------------------
@general_bp.route('/chat', methods=['POST'])
def chat():
    # Obtener el identificador del usuario desde la sesión
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
        response = obtener_respuesta(user_email, user_message)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
