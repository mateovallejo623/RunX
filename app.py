from fastapi import FastAPI, Header, HTTPException, Request
import os
from scraper.main import scrapeo
from bot.plan import generar_plan

app = FastAPI()

@app.post("/scrap")
async def run_scraping(x_api_key: str = Header(None)):
    expected_key = os.environ.get("SCRAPER_API_KEY")
    if x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Unauthorized")
    resultado = scrapeo()
    return {"mensaje": resultado}

@app.post("/plan")
async def handle_plan(request: Request):
    data = await request.json()
    respuesta = generar_plan(data)
    return {"respuesta": respuesta}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
