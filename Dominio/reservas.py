from flask import Blueprint, jsonify, render_template, request, session, flash, url_for, redirect
from Persistencia.AgenteBD import MongoDBAgent
from Persistencia.DAOS.ReservasDAO import ReservasDAO
from bson import ObjectId
from datetime import datetime, date

mongo_agent = MongoDBAgent()
reservas_bp = Blueprint('reservas', __name__)

@reservas_bp.route('/', methods=['POST'])
def crear_reserva():
    # Validación de autenticación del usuario
    if 'user_id' not in session:
        # Usuario no autenticado: se solicita iniciar sesión
        return """
        <script>
            alert("Debes iniciar sesión para reservar.");
            window.history.back();
        </script>
        """
    
    user_name = session.get("user_name", None)
    # Obtener información del usuario (se verifica que no sea "Anónimo" y tenga rol "Tourist")
    from Persistencia.DAOS.UserDAO import UserDAO
    usuario = UserDAO.obtener_dato({"_id": ObjectId(session["user_id"])})
    if not user_name or user_name == "Anónimo" or usuario.get("type") != "Tourist":
        return """
        <script>
            alert("No se puede realizar la reserva si eres Anónimo o no tienes el rol de Tourist. Por favor, inicia sesión o regístrate.");
            window.history.back();
        </script>
        """
    
    # Recoger datos del formulario
    hotel_id = request.form.get("hotel_id")
    start_str = request.form.get("startDate")
    end_str = request.form.get("endDate")
    num_persons = request.form.get("numPersons", "0")

    # Validación de campos obligatorios
    if not hotel_id or not start_str or not end_str:
        return "Faltan campos obligatorios", 400

    # Verificar existencia del hotel
    hotel_info = mongo_agent.db["hoteles"].find_one({"_id": ObjectId(hotel_id)})
    if not hotel_info:
        return "Hotel no encontrado", 404

    try:
        # Parseo de fechas desde el formulario
        start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
    except ValueError:
        error_msg = "Formato de fecha inválido."
        return redirect(url_for('reservas.reservar_page', hotel_id=hotel_id, error=error_msg))

    # Validar que la fecha de fin sea posterior a la de inicio
    if end_date <= start_date:
        error_msg = "La fecha de fin debe ser posterior a la de inicio."
        return redirect(url_for('reservas.reservar_page', hotel_id=hotel_id, error=error_msg))

    # Validar que la fecha de inicio no esté en el pasado
    hoy = date.today()
    if start_date < hoy:
        error_msg = "No puedes reservar en una fecha pasada."
        return redirect(url_for('reservas.reservar_page', hotel_id=hotel_id, error=error_msg))

    # Verificar solapamiento con reservas existentes
    reservas_cursor = ReservasDAO.obtener_reservas_por_hotel(hotel_id)
    for r in reservas_cursor:
        try:
            r_start = datetime.strptime(r["fecha_inicio"], "%Y-%m-%d").date()
            r_end = datetime.strptime(r["fecha_fin"], "%Y-%m-%d").date()
        except (KeyError, ValueError):
            # Registrar o continuar si la fecha no es válida
            continue
        if (start_date < r_end) and (end_date > r_start):
            error_msg = "El hotel ya está reservado en ese rango de fechas."
            return redirect(url_for('reservas.reservar_page', hotel_id=hotel_id, error=error_msg))

    # Preparar documento de reserva
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

    # Actualizar contador de reservas del hotel
    mongo_agent.db["hoteles"].update_one(
        {"_id": ObjectId(hotel_id)},
        {"$inc": {"reservas_count": 1}}
    )

    flash("Reserva creada satisfactoriamente.")
    return redirect(url_for('reservas.reserva_confirmada'))

@reservas_bp.route('/reservar/<hotel_id>')
def reservar_page(hotel_id):
    """Muestra el formulario de reserva para un hotel concreto."""
    hotel = mongo_agent.db["hoteles"].find_one({"_id": ObjectId(hotel_id)})
    if not hotel:
        return "Hotel no encontrado", 404

    # Convertir ObjectId a cadena
    hotel["_id"] = str(hotel["_id"])
    error_message = request.args.get("error", "")
    return render_template("reservar.html", hotel=hotel, error_message=error_message)

@reservas_bp.route('/reserva_confirmada')
def reserva_confirmada():
    # Página de confirmación de reserva
    return render_template("reserva_confirmada.html")