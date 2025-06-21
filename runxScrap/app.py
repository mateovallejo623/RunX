# app.py
from fastapi import FastAPI, Header, HTTPException
from main import scrapeo
import os

app = FastAPI()

@app.post("/scrap")
async def run_scraping(x_api_key: str = Header(None)):
    expected_key = os.environ.get("SCRAPER_API_KEY")

    if x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Unauthorized")

    resultado = scrapeo()
    return {"mensaje": resultado}
