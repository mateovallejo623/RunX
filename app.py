from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import psycopg2
import bcrypt
from scraper.main import scrapeo
from bot.plan import generar_plan

# --- DB CONNECTION ---
conn = psycopg2.connect(
    host=os.getenv("SUPABASE_DB_HOST"),
    port=os.getenv("SUPABASE_DB_PORT"),
    user=os.getenv("SUPABASE_DB_USER"),
    password=os.getenv("SUPABASE_DB_PASS"),
    dbname=os.getenv("SUPABASE_DB_NAME")
)
conn.autocommit = True
cursor = conn.cursor()

# --- FASTAPI APP ---
app = FastAPI()

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://preview--runx-race-ready.lovable.app"],  # Dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SCHEMAS ---
class RegisterUser(BaseModel):
    email: str
    password: str

class LoginUser(BaseModel):
    email: str
    password: str

# --- RUTA: Registro ---
@app.post("/auth/register")
def register(user: RegisterUser):
    cursor.execute("SELECT id FROM users WHERE email = %s", (user.email,))
    if cursor.fetchone():
        raise HTTPException(status_code=400, detail="Email ya registrado")

    hashed_pw = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    cursor.execute(
        "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id",
        (user.email, hashed_pw)
    )
    user_id = cursor.fetchone()[0]
    return {"message": "Usuario registrado correctamente", "user_id": user_id}

# --- RUTA: Login ---
@app.post("/auth/login")
def login(user: LoginUser):
    cursor.execute("SELECT id, password_hash FROM users WHERE email = %s", (user.email,))
    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    user_id, password_hash = result
    if not bcrypt.checkpw(user.password.encode("utf-8"), password_hash.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    return {"message": "Login exitoso", "user_id": user_id}

# --- RUTA: Scraping ---
@app.post("/scrap")
async def run_scraping(x_api_key: str = Header(None)):
    expected_key = os.environ.get("SCRAPER_API_KEY")
    if x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Unauthorized")
    resultado = scrapeo()
    return {"mensaje": resultado}

# --- RUTA: Generar plan de entrenamiento ---
@app.post("/plan")
async def handle_plan(request: Request):
    data = await request.json()
    respuesta = generar_plan(data)
    return {"respuesta": respuesta}

# --- RUN APP (solo para desarrollo local) ---
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
