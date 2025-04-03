import os
import requests
from flask import Blueprint, render_template, request, jsonify
from dotenv import load_dotenv

# Cargar variables de entorno (si aún no se han cargado en el main)
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

# Crear el blueprint para mapas y navegación
maps_bp = Blueprint('maps', __name__)

# Clave de la API de Google Maps (Routes API)
ROUTES_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# ----------------------------------------------------------------------
# POST /get-route
# Llamada a la Routes API para obtener la polyline de una ruta
# ----------------------------------------------------------------------
@maps_bp.route("/get-route", methods=["POST"])
def get_route():
    data = request.json
    origin = data.get("origin")
    destination = data.get("destination")
    
    if not origin or not destination:
        return jsonify({"error": "Origin/destination missing"}), 400

    payload = {
        "origin": {"location": {"latLng": origin}},
        "destination": {"location": {"latLng": destination}},
        "travelMode": "DRIVE"
    }

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

# ----------------------------------------------------------------------
# GET /map
# Página que muestra el mapa
# ----------------------------------------------------------------------
@maps_bp.route("/map")
def map_page():
    google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    return render_template("map.html", google_maps_api_key=google_maps_api_key)

# ----------------------------------------------------------------------
# GET /
# Página principal (index) que puede incluir elementos de navegación
# ----------------------------------------------------------------------
@maps_bp.route("/")
def index():
    google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    return render_template("index.html", google_maps_api_key=google_maps_api_key)
