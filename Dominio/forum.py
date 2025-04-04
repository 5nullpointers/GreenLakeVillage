import os
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename

from Persistencia.AgenteBD import MongoDBAgent

# Instanciar el agente de MongoDB
mongo_agent = MongoDBAgent()

# Crear el blueprint para el foro
forum_bp = Blueprint('forum', __name__)

# -----------------------------------------------------------------
# POST /api/admin/crear-tema
# Creación de un tema (posiblemente restringido a administradores)
# -----------------------------------------------------------------
@forum_bp.route('/api/admin/crear-tema', methods=['POST'])
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
    if result.inserted_id:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False}), 500

# ----------------------------------------------------
# GET /api/foro/temas
# Listado de temas del foro
# ----------------------------------------------------
@forum_bp.route('/api/foro/temas', methods=['GET'])
def api_foro_temas():
    temas = list(mongo_agent.db["temas_forum"].find({}))
    for tema in temas:
        tema["_id"] = str(tema["_id"])
    return jsonify(temas)

# ---------------------------------------------------------------------
# GET /api/foro/temas/<string:tema_id>/comentarios
# Comentarios asociados a un tema
# ---------------------------------------------------------------------
@forum_bp.route('/api/foro/temas/<string:tema_id>/comentarios', methods=['GET'])
def api_foro_comentarios(tema_id):
    comentarios = list(mongo_agent.db["comentarios_forum"].find({"tema_id": tema_id}))
    for c in comentarios:
        c["_id"] = str(c["_id"])
    return jsonify(comentarios)

# ---------------------------------------------------------------------
# POST /api/foro/comentar
# Publicar un comentario en el foro
# ---------------------------------------------------------------------
@forum_bp.route('/api/foro/comentar', methods=['POST'])
def api_foro_comentar():
    tema_id = request.form.get("tema_id")
    comentario_texto = request.form.get("comentario")
    autor = session.get("user_name", "Anónimo")
    imagen_url = None

    # Manejar la imagen si se envió
    if 'imagen' in request.files:
        file = request.files['imagen']
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Definir la carpeta de subida (ajusta la ruta según tu estructura)
            UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'Presentacion', 'static', 'uploads')
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
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
        return jsonify({"success": True})
    else:
        return jsonify({"success": False}), 500