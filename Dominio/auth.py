from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

# Importa los DAO y agentes según la estructura de tu proyecto
from Persistencia.DAOS.UserDAO import UserDAO
from Persistencia.AgenteBD import MongoDBAgent

# Si necesitas usar el agente de Mongo, puedes instanciarlo (o importarlo desde otro módulo central)
mongo_agent = MongoDBAgent()

auth_bp = Blueprint('auth', __name__)

# -------------------------------
# GET /login - Página de login
# -------------------------------
@auth_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('loginRegister.html')

# -------------------------------
# POST /login - Proceso de autenticación
# -------------------------------
@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        flash("Por favor, completa ambos campos.")
        return redirect(url_for('auth.login_page'))

    usuario = UserDAO.obtener_dato({"email": email})
    if usuario:
        if usuario.get("blocked") == True:
            return redirect(url_for('auth.UserBlock'))

        user_type = usuario.get("type")
        if user_type == "Tourist":
            if check_password_hash(usuario.get("pass"), password):
                session['user_id'] = str(usuario["_id"])
                session['user_name'] = usuario.get("name")
                flash("Inicio de sesión exitoso!")
                return redirect(url_for('maps.map_page'))
            else:
                flash("Contraseña incorrecta.")
                return redirect(url_for('auth.login_page'))
        elif user_type == "Admin":
            if check_password_hash(usuario.get("pass"), password):
                session['user_id'] = str(usuario["_id"])
                session['user_name'] = usuario.get("name")
                flash("Inicio de sesión exitoso!")
                return redirect(url_for('admin.admin'))  # Asegúrate de que este endpoint exista
            else:
                flash("Contraseña incorrecta.")
                return redirect(url_for('auth.login_page'))
        elif user_type == "BusinessOwner":
            if check_password_hash(usuario.get("pass"), password):
                session['user_id'] = str(usuario["_id"])
                session['user_name'] = usuario.get("name")
                flash("Inicio de sesión exitoso!")
                return redirect(url_for('propietarios.Propietarios'))  # Asegúrate de que este endpoint exista
            else:
                flash("Contraseña incorrecta.")
                return redirect(url_for('auth.login_page'))
        else:
            flash("Tipo de usuario desconocido.")
            return redirect(url_for('auth.login_page'))
    else:
        flash("Usuario no encontrado.")
        return redirect(url_for('auth.login_page'))

# -------------------------------
# POST /register - Registro de nuevos usuarios
# -------------------------------
@auth_bp.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')

    if not name or not email or not password:
        flash("Todos los campos son obligatorios.")
        return redirect(url_for('auth.login_page'))

    if UserDAO.obtener_dato({"email": email}):
        flash("El correo ya está registrado.")
        return redirect(url_for('auth.login_page'))

    hashed_password = generate_password_hash(password)
    nuevo_usuario = {
        "name": name,
        "email": email,
        "pass": hashed_password,
        "type": "Tourist",
        "blocked": False,
        "preferencias": [],
        "retos_completados": [],
        "tokens": 0
    }
    UserDAO.insertar_dato(nuevo_usuario)

    usuario = UserDAO.obtener_dato({"email": email})
    if usuario:
        session['user_id'] = str(usuario["_id"])
        session['user_name'] = usuario.get("name")
    else:
        flash("Error en el registro")
        return redirect(url_for('auth.login_page'))

    flash("Registro exitoso. Ahora elige tus preferencias.")
    return redirect(url_for('auth.preferences', user_email=email))

# -------------------------------
# GET y POST /preferences - Gestión de preferencias de usuario
# -------------------------------
@auth_bp.route('/preferences', methods=['GET', 'POST'])
def preferences():
    user_email = request.args.get('user_email')
    usuario = UserDAO.obtener_dato({"email": user_email})

    if request.method == 'POST':
        # Recibir las preferencias desde el formulario
        preferences = request.form.getlist('preferences')
        UserDAO.actualizar_dato({"email": user_email}, {"preferencias": preferences})
        flash("Tus preferencias se han guardado correctamente.")
        return redirect(url_for('maps.map_page'))
    
    return render_template('Preferences.html', user=usuario)

# -------------------------------
# POST /save-preferences - Guardar preferencias vía petición JSON
# -------------------------------
@auth_bp.route('/save-preferences', methods=['POST'])
def save_preferences():
    data = request.json
    user_id = session.get('user_id')
    preferences = data.get('preferencias')

    if not user_id or not preferences:
        return jsonify({"error": "Email o preferencias no proporcionadas"}), 400

    try:
        user = UserDAO.obtener_dato({"_id": ObjectId(user_id)})
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 400

        result = UserDAO.actualizar_dato({"_id": ObjectId(user_id)}, {"preferencias": preferences})
        if result.modified_count > 0:
            return jsonify({"success": True, "redirect": url_for('maps.map_page')})
        else:
            return jsonify({"error": "No se pudo actualizar las preferencias"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------------
# GET /UserBlock - Página para usuarios bloqueados
# -------------------------------
@auth_bp.route('/UserBlock', methods=['GET'])
def UserBlock():
    return render_template('UserBlocked.html')

# -------------------------------
# GET /users - Listado de todos los usuarios (gestión de usuarios)
# -------------------------------
@auth_bp.route('/users', methods=['GET'])
def users():
    usuarios = UserDAO.obtener_todos()
    return jsonify(usuarios), 200