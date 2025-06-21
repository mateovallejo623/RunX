import requests
from bs4 import BeautifulSoup
from supabase import create_client
import os

# 1. Conectar con Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
print("🔌 Conectado a Supabase")

# 2. Limpiar la tabla existente
supabase.table("Races").delete().gt("id", 0).execute()

# 3. Scrapeo desde la web
BASE_URL = "https://clubdecorredores.com"
url = f"{BASE_URL}/carreras/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}
response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("✅ Página cargada correctamente")
else:
    print(f"❌ Error al cargar página. Status code: {response.status_code}")

soup = BeautifulSoup(response.text, "html.parser")

# 4. Buscar cada card de carrera
target_substring = "col-xs-12 col-sm-6 col-md-4 col-lg-3 cajaIndividual element-item"
cards = soup.findcards = soup.find_all("div", class_=lambda c: c and target_substring in " ".join(c if isinstance(c, list) else [c]))
print(f"🔍 Se encontraron {len(cards)} cards de carreras")

for index, card in enumerate(cards):
    try:
        # Banner
        banner_img = card.find("div", class_="bannerCarrera").find("img")["src"]
        banner = BASE_URL + banner_img if banner_img.startswith("/") else banner_img

        # Link de inscripción
        registration_tag = card.find_parent("a")
        registrationLink = registration_tag["href"] if registration_tag and registration_tag.has_attr("href") else ""

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

        print(f"📦 Procesando {index+1}: {name} | {date} | {lugar} | {distancias}")

    except Exception as e:
        print(f"⚠️ Error al procesar una carrera: {e}")

        # Insertar en Supabase
        supabase.table("Races").insert({
            "name": name,
            "date": date,
            "location": lugar,
            "distances": distancias,
            "banner": banner,
            "registrationLink": registrationLink
        }).execute()

        print(f"✅ Insertado correctamente: {insert_response}")

BASE_URL2 = "https://www.corro.com.ar"
url2 = f"{BASE_URL2}/carreras/"
headers2 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}
response2 = requests.get(url2, headers=headers2)

STEP = 8
MAX_START = 24  

for start in range(0, MAX_START + 1, STEP):
    # Armar la URL según el índice
    url = f"{url2}?start={start}" if start > 0 else f"{url2}?limitstart=0"
    print(f"\n🔗 Scrapeando: {url}")

    response2 = requests.get(url, headers=headers2)
    if response2.status_code != 200:
        print(f"❌ Error al cargar {url}")
        continue

    soup = BeautifulSoup(response2.text, "html.parser")

    # Buscar cards
    cards = soup.find_all("div", class_=lambda c: c and "itemContainer col-sm-6" in c)
    print(f"✅ Se encontraron {len(cards)} cards en {url}")

    for idx, card in enumerate(cards):
        try:
            print(f"\n📦 Procesando card #{idx + 1}")

            # Banner
            img_tag = card.find("img")
            banner = BASE_URL2 + img_tag["src"] if img_tag and img_tag.has_attr("src") else ""

            # <strong> tags: 0 = name, 1 = date, 2 = location, 4 = distances
            strongs = card.find_all("strong")
            name = strongs[0].get_text(strip=True) if len(strongs) > 0 else ""
            date = strongs[1].get_text(strip=True) if len(strongs) > 1 else ""
            location = strongs[2].get_text(strip=True) if len(strongs) > 2 else ""
            distances = strongs[4].get_text(strip=True) if len(strongs) > 4 else ""

            print(f"🏁 {name} | 📅 {date} | 📍 {location} | 🏃 {distances}")

            # Subir a Supabase
            supabase.table("Races").insert({
                "name": name,
                "date": date,
                "location": location,
                "distances": distances,
                "banner": banner,
                "registrationLink": url
            }).execute()

        except Exception as e:
            print(f"⚠️ Error al procesar una carrera: {e}")