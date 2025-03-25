import os
from openai import OpenAI

# Cargar la clave de API desde la variable de entorno
openai_api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=openai_api_key)

def obtener_respuesta(pregunta):
    prompt = f"Eres un experto en el capitales'. Responde de forma corta y precisa a la siguiente pregunta: {pregunta}"
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": ""},
            {"role": "user", "content": prompt}
        ]
    )

    return completion.choices[0].message.content.strip()

print(obtener_respuesta("¿Cuál es la capital de Francia?"))