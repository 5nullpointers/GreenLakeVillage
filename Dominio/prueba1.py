from dotenv import load_dotenv
import os
import openai
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__,
            static_folder='../Presentacion/static',
            template_folder='../Presentacion/templates')

# Cargar variables de entorno desde .env
load_dotenv()

# Clave de la API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route('/')
def home():
    # Ruta de la página de inicio
    # Renderiza loginRegister.html
    return render_template('loginRegister.html')


@app.route('/prueba')
def prueba():
    return render_template('Prueba1.html')

@app.route('/admin')
def admin():
    return render_template('Admin.html')


@app.route('/login', methods=['POST'])
def login():
    # Aquí agregarías la lógica para comprobar los datos del usuario
    # Por ahora, redirigimos al home (loginRegister.html)
    return redirect(url_for('home'))


@app.route('/register', methods=['POST'])
def register():
    # Agregar la lógica para almacenar los datos del usuario
    # Por ahora, simulamos que el registro fue exitoso y redirigimos al login
    return redirect(url_for('home'))


MAX_HISTORY = 5
conversation_history = []


@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message")

    if not user_message:
        return jsonify({"error": "Mensaje vacío"}), 400

    try:
        client = openai.OpenAI()

        # Agregar el nuevo mensaje al historial
        conversation_history.append({"role": "user", "content": user_message})

        # Limitar el historial solo a los últimos MAX_HISTORY mensajes
        # Multiplicamos por 2 porque cada mensaje tiene respuesta de la IA
        conversation_history_trimmed = conversation_history[-(
            MAX_HISTORY * 2):]

        # Crear el mensaje con el historial recortado
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Eres un asistente virtual para facilitar ayuda turística de rutas y hoteles..."}
            ] + conversation_history_trimmed
        )

        chat_response = response.choices[0].message.content

        # Agregar la respuesta de la IA al historial
        conversation_history.append(
            {"role": "assistant", "content": chat_response})

        return jsonify({"response": chat_response})

    except openai.OpenAIError as e:
        return jsonify({"error": f"Error en OpenAI: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error desconocido: {str(e)}"}), 500


if __name__ == '__main__':
    # Escucha en todas las IPs (0.0.0.0) y puerto 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
