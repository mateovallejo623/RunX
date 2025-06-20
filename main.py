import requests
from bs4 import BeautifulSoup
from supabase import create_client
import os

# 1. Conectar con Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. Limpiar la tabla existente
supabase.table("Races").delete().execute()

# 3. Scrapeo desde la web
BASE_URL = "https://clubdecorredores.com"
url = f"{BASE_URL}/carreras/"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# 4. Buscar cada card de carrera
target_class = "col-xs-12 col-sm-6 col-md-4 col-lg-3 cajaIndividual element-item c1"
cards = soup.find_all("div", class_=lambda c: c and " ".join(c) == target_class)

for card in cards:
    try:
        # Banner
        banner_img = card.find("div", class_="bannerCarrera").find("img")["src"]
        banner = BASE_URL + banner_img if banner_img.startswith("/") else banner_img

        # Link de inscripción
        registration_tag = card.find_parent("a")
        registrationLink = BASE_URL + registration_tag["href"] if registration_tag and registration_tag.has_attr("href") else ""

        # Nombre de la carrera
        name_tag = card.find("div", class_="tituloC")
        name = name_tag.get_text(strip=True) if name_tag else ""

        # Fecha
        date_tag = card.find("div", class_="fechaCarrera2")
        date = date_tag.get_text(strip=True) if date_tag else ""

        # Distancias
        distancias = ""
        lugar = ""
        lugar_tags = card.find_all("div", class_="lugardistC")
        if lugar_tags:
            ps = lugar_tags[0].find_all("p")
            if len(ps) >= 1:
                distancias = ps[0].get_text(strip=True)
            if len(ps) >= 2:
                lugar = ps[1].get_text(strip=True)

        # Insertar en Supabase
        supabase.table("Races").insert({
            "name": name,
            "date": date,
            "location": lugar,
            "distances": distancias,
            "banner": banner,
            "registrationLink": registrationLink
        }).execute()

    except Exception as e:
        print(f"⚠️ Error al procesar una carrera: {e}")
