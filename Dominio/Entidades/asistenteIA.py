import os
from openai import OpenAI
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from Persistencia.AgenteBD import MongoDBAgent

# Cargar la clave de API desde la variable de entorno
openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)

def obtener_respuesta(user_email, mensaje):
    # Conectar a MongoDB usando tu agente
    agent = MongoDBAgent()
    
    # Obtener datos desde las colecciones de MongoDB
    usuario = agent.find_one("usuarios", {"email": user_email})
    hoteles = agent.find("hoteles")
    restaurantes = agent.find("restaurantes")
    rutas = agent.find("rutas_turisticas")

    if usuario is None:
        return "Usuario no encontrado en la base de datos."

    # Construir información del usuario
    usuario_info = f"Nombre: {usuario.get('name', 'Desconocido')}\n"
    preferencias = usuario.get('preferencias', [])
    if not preferencias:
        usuario_info += "Preferencias: No especificadas\n\n"
    else:
        usuario_info += f"Preferencias: {', '.join(preferencias)}\n\n"

    # Construir información de hoteles
    hoteles_info = "Datos de Hoteles:\n"
    for hotel in hoteles:
        hoteles_info += (
            f"- {hotel.get('nombre', 'Sin nombre')}: Precio: {hotel.get('precio', 'N/A')}, "
            f"Servicios: {', '.join(hotel.get('servicios', []))}, "
            f"Atracciones: {', '.join(hotel.get('atraccionesCercanas', []))}, "
            f"Restaurantes Cercanos: {', '.join(hotel.get('restaurantesCercanos', []))}, "
            f"Eventos: {', '.join(hotel.get('eventosProximos', []))}\n"
        )
    hoteles_info += "\n"

    # Construir información de restaurantes
    restaurantes_info = "Datos de Restaurantes:\n"
    for r in restaurantes:
        restaurantes_info += (
            f"- {r.get('nombre', 'Sin nombre')}: Precio Medio: {r.get('precio_medio', 'N/A')}, "
            f"Servicios: {', '.join(r.get('servicios', []))}, "
            f"Especialidades: {', '.join(r.get('especialidades', []))}, "
            f"Eventos: {', '.join(r.get('eventosProximos', []))}\n"
        )
    restaurantes_info += "\n"

    # Construir información de rutas turísticas
    rutas_info = "Datos de Rutas Turísticas:\n"
    for ruta in rutas:
        rutas_info += (
            f"- {ruta.get('ruta_nombre', 'Sin nombre')}: Tipo: {ruta.get('tipo_ruta', '')}, "
            f"Longitud: {ruta.get('longitud_km', '')} km, Duración: {ruta.get('duracion_hr', '')} horas, "
            f"Popularidad: {ruta.get('popularidad', '')}\n"
        )
    rutas_info += "\n"

    # Construir el prompt completo
    prompt = f"""
Eres un asistente turístico experto para nuestra ciudad inventada "GreenLake city". Tienes acceso a los siguientes datos:

Datos del usuario:
{usuario_info}

{hoteles_info}
{restaurantes_info}
{rutas_info}

Responde a la siguiente consulta del usuario: "{mensaje}"

Basándote en estos datos y en las preferencias del usuario, sugiere de forma corta y precisa:
1. Dónde hospedarse.
2. Dónde comer.
3. Qué ruta turística realizar en "GreenLake city".
    """

    # (Opcional) Imprimir el prompt para depuración
    # print(prompt)
    
    # Enviar el prompt a la API de OpenAI
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": ""},
            {"role": "user", "content": prompt}
        ]
    )

    respuesta = completion.choices[0].message.content.strip()
    
    # Cerrar la conexión con la base de datos (opcional)
    agent.close_connection()

    return respuesta


if __name__ == "__main__":
    # Ejemplo de uso: obtener respuesta para el usuario "joseluis@gmail.com" y su consulta
    respuesta = obtener_respuesta("lucia@gmail.com", "¿Qué puedo hacer hoy?")
    print("Respuesta de la IA:")
    print(respuesta)
