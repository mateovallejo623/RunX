from fastapi import FastAPI, Request, Header, HTTPException
import openai
import os
from main import scrapeo

openai.api_key = os.environ.get("OPENAI_API_KEY")

app = FastAPI()

@app.post("/plan")
async def entrenador_virtual(request: Request):
    data = await request.json()

    carrera = data.get("carrera", "")
    distancia = data.get("distancia", "")
    lugar = data.get("lugar", "")
    fecha = data.get("fecha", "")
    mensaje_usuario = data.get("mensaje_usuario", "")

    # Generar prompt completo
    prompt_inicial = f"""Sos un entrenador virtual de running, especializado en carreras. El usuario está interesado en esta carrera:
- Nombre: {carrera}
- Distancia: {distancia}
- Lugar: {lugar}
- Fecha: {fecha}

Comenzá la conversación como si ya te hubiera saludado. No digas "Hola soy un modelo de IA". Mostrate entusiasta y profesional.

Si este es su primer mensaje, respondé esto:
"¡Hola! Soy tu entrenador virtual especializado en carreras. Veo que estás interesado en la carrera '{carrera}' de {distancia} en {lugar} el {fecha}. Te ayudaré a crear un plan de entrenamiento personalizado. Para empezar, cuéntame:
- ¿Cuál es tu nivel actual de running?
- ¿Cuántos días a la semana puedes entrenar?
- ¿Tienes alguna lesión o limitación?
- ¿Cuál es tu objetivo para esta carrera?"

Si ya respondió eso, continuá la conversación de forma natural con recomendaciones claras y realistas.

Mensaje del usuario:
\"{mensaje_usuario}\"
"""

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt_inicial}
            ]
        )
        respuesta = completion.choices[0].message.content
        return {"respuesta": respuesta}

    except Exception as e:
        return {"error": str(e)}


@app.post("/scrap")
async def run_scraping(x_api_key: str = Header(None)):
    # Comparar la clave recibida con la de entorno
    expected_key = os.environ.get("SCRAPER_API_KEY")

    if x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Unauthorized")

    resultado = scrapeo()
    return {"mensaje": resultado}
    
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Railway setea PORT como env var
    uvicorn.run("app:app", host="0.0.0.0", port=port)