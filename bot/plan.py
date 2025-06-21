import openai
import os

openai.api_key = os.environ.get("OPENAI_API_KEY")

def generar_plan(data):
    carrera = data.get("carrera", "")
    distancia = data.get("distancia", "")
    lugar = data.get("lugar", "")
    fecha = data.get("fecha", "")
    mensaje_usuario = data.get("mensaje_usuario", "")

    prompt = f"""Sos un entrenador virtual de running. El usuario te habló sobre esta carrera:
- Nombre: {carrera}
- Distancia: {distancia}
- Lugar: {lugar}
- Fecha: {fecha}

quiere obtener un plan de entrenamiento en base a la información personal que te está enviando. dale un plan en base a la fecha actual y la fecha de la carrera y a sus caracteristicas.

Mensaje del usuario:
\"{mensaje_usuario}\"

Respondé de forma profesional y clara con consejos realistas y personalizados.
"""

    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return completion.choices[0].message.content