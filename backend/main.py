import os
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import random
from dotenv import load_dotenv
import motor.motor_asyncio
import json
from pydantic import BaseModel
from contextlib import asynccontextmanager

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    if await airports_collection.count_documents({}) == 0:
        print("🔧 Inicjalizacja bazy danych słowników z pliku data.json...")
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("airports"):
                    await airports_collection.insert_many(data["airports"])
                if data.get("destinations"):
                    await destinations_collection.insert_many(data["destinations"])
            print("✅ Baza słowników została poprawnie zasilona (Seeding)!")
        except Exception as e:
            print(f"⚠️ Błąd podczas wczytywania data.json: {e}")
    else:
        print("✅ Baza słowników ma już dane, pomijam inicjalizację.")
    yield

app = FastAPI(title="Smart Travel Planner API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.travel_planner
weather_collection = db.weather_cache
airports_collection = db.airports
destinations_collection = db.destinations

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
@app.get("/")
async def root():
    return {"message": "Backend działa! Witaj w Smart Travel Planner."}


@app.get("/api/airports")
async def get_airports():
    airports = await airports_collection.find({}, {"_id": 0}).to_list(length=200)
    return airports

@app.get("/api/destinations")
async def get_destinations():
    destinations = await destinations_collection.find({}, {"_id": 0}).to_list(length=200)
    return destinations

hotels_collection = db.hotels_cache


@app.get("/api/hotels")
async def get_hotels(city: str, check_in: str, check_out: str):
    cache_key = f"{city.lower()}-{check_in}-{check_out}"
    cached_hotels = await hotels_collection.find_one({"cache_key": cache_key})
    if cached_hotels:
        last_updated = cached_hotels.get("updated_at")
        if last_updated:
            if last_updated.tzinfo is None:
                last_updated = last_updated.replace(tzinfo=timezone.utc)
            if (datetime.now(timezone.utc) - last_updated) < timedelta(hours=24):
                if cached_hotels.get("data"):
                    print("✅ Zwracam HOTELE z bazy danych (Cache)!")
                    return {"data": cached_hotels["data"]}

    print(f"🏨 Szukam hoteli dla: {city} ({check_in} do {check_out})")

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "booking-com15.p.rapidapi.com"
    }

    parsed_hotels = []

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            dest_response = await client.get(
                "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination",
                headers=headers,
                params={"query": city}
            )
            dest_data = dest_response.json().get("data", [])

            if dest_data:
                dest_id = dest_data[0]["dest_id"]
                search_type = dest_data[0]["search_type"]

                hotel_params = {
                    "dest_id": dest_id,
                    "search_type": search_type,
                    "arrival_date": check_in,
                    "departure_date": check_out,
                    "adults": "1",
                    "room_qty": "1",
                    "page_number": "1",
                    "currency_code": "PLN"
                }

                hotel_response = await client.get(
                    "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels",
                    headers=headers,
                    params=hotel_params
                )

                if hotel_response.status_code == 200:
                    hotels_raw = hotel_response.json().get("data", {}).get("hotels", [])
                    for h in hotels_raw[:5]:
                        parsed_hotels.append({
                            "name": h["property"]["name"],
                            "rating": h["property"].get("reviewScore", "Brak oceny"),
                            "price": h["property"]["priceBreakdown"]["grossPrice"]["value"],
                            "currency": "PLN"
                        })
                else:
                    print(f"⚠️ Booking.com API zwróciło status: {hotel_response.status_code}")
            else:
                print(f"⚠️ Nie znaleziono miasta {city} w bazie Booking.com")

    except Exception as e:
        print(f"⚠️ Błąd połączenia z API hoteli: {e}")

    if not parsed_hotels:
        print("⚠️ Generuję losowe HOTELE (Fallback).")
        typy_obiektów = ["Grand Hotel", "Apartamenty Centrum", "Boutique Hotel", "Resort & Spa", "Hostel"]

        for i in range(4):
            parsed_hotels.append({
                "name": f"{random.choice(typy_obiektów)} {city.capitalize()}",
                "rating": round(random.uniform(6.5, 9.8), 1),
                "price": random.randint(400, 3500),
                "currency": "PLN"
            })

    await hotels_collection.update_one(
        {"cache_key": cache_key},
        {"$set": {"cache_key": cache_key, "data": parsed_hotels, "updated_at": datetime.now(timezone.utc)}},
        upsert=True
    )

    return {"data": parsed_hotels}

flights_collection = db.flights_cache

@app.get("/api/flights")
async def get_flights(origin: str, destination: str, date: str):
    if not RAPIDAPI_KEY:
        raise HTTPException(status_code=500, detail="Brak klucza RAPIDAPI_KEY w .env")

    cache_key = f"{origin.lower()}-{destination.lower()}-{date}"

    cached_flights = await flights_collection.find_one({"cache_key": cache_key})
    if cached_flights:
        last_updated = cached_flights.get("updated_at")
        if last_updated:
            if last_updated.tzinfo is None:
                last_updated = last_updated.replace(tzinfo=timezone.utc)
            if (datetime.now(timezone.utc) - last_updated) < timedelta(hours=2):
                if cached_flights.get("data"):
                    print("✅ Zwracam LOTY z bazy danych (Cache)!")
                    return {"data": cached_flights["data"]}

    print(f"✈️ Szukam lotów w RapidAPI dla: {origin} -> {destination} na {date}")

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "sky-scrapper.p.rapidapi.com"
    }

    parsed_flights = []
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            orig_resp = await client.get("https://sky-scrapper.p.rapidapi.com/api/v1/flights/searchAirport",
                                         headers=headers, params={"query": origin})
            orig_data = orig_resp.json().get("data", [])

            dest_resp = await client.get("https://sky-scrapper.p.rapidapi.com/api/v1/flights/searchAirport",
                                         headers=headers, params={"query": destination})
            dest_data = dest_resp.json().get("data", [])


            if orig_data and dest_data:
                orig_sky_id = orig_data[0]["skyId"]
                orig_entity_id = orig_data[0]["entityId"]
                dest_sky_id = dest_data[0]["skyId"]
                dest_entity_id = dest_data[0]["entityId"]

                flight_params = {
                    "originSkyId": orig_sky_id,
                    "destinationSkyId": dest_sky_id,
                    "originEntityId": orig_entity_id,
                    "destinationEntityId": dest_entity_id,
                    "date": date,
                    "currency": "PLN"
                }

                flight_resp = await client.get("https://sky-scrapper.p.rapidapi.com/api/v1/flights/searchFlights",
                                               headers=headers, params=flight_params)

                if flight_resp.status_code == 200:
                    raw_flights_data = flight_resp.json()
                    itineraries = raw_flights_data.get("data", {}).get("itineraries", [])

                    for it in itineraries[:5]:
                        leg = it["legs"][0]
                        parsed_flights.append({
                            "id": it["id"],
                            "airline": leg["carriers"]["marketing"][0]["name"] if leg["carriers"][
                                "marketing"] else "Nieznana",
                            "departure_time": leg["departure"].split("T")[1][:5],
                            "arrival_time": leg["arrival"].split("T")[1][:5],
                            "price": it["price"]["raw"]
                        })
                else:
                    print(f"⚠️ Sky Scrapper API zwróciło problematyczny status: {flight_resp.status_code}")
            else:
                print("⚠️ Nie znaleziono kodów lotnisk w bazie RapidAPI")

    except Exception as e:
        print(f"⚠️ Błąd (np. timeout) połączenia z API lotów: {e}")


    if not parsed_flights:
        print("⚠️ Generuję losowe LOTY (Fallback).")
        linie_lotnicze = ["Ryanair", "Wizz Air", "LOT Polish Airlines", "Lufthansa", "Air France", "KLM"]

        for i in range(3):
            godzina_wylotu = random.randint(6, 18)
            godzina_przylotu = godzina_wylotu + random.randint(1, 4)
            minuty = random.choice(["00", "15", "30", "45"])

            parsed_flights.append({
                "id": f"mock-flight-{random.randint(1000, 9999)}",
                "airline": random.choice(linie_lotnicze),
                "departure_time": f"{godzina_wylotu:02d}:{minuty}",
                "arrival_time": f"{godzina_przylotu:02d}:{minuty}",
                "price": random.randint(250, 1500)
            })

    await flights_collection.update_one(
        {"cache_key": cache_key},
        {"$set": {"cache_key": cache_key, "data": parsed_flights, "updated_at": datetime.now(timezone.utc)}},
        upsert=True
    )

    return {"data": parsed_flights}

@app.get("/api/weather/{city}")
async def get_weather(city: str, start_date: str, days: int):
    if not WEATHER_API_KEY:
        raise HTTPException(status_code=500, detail="Brak klucza API do pogody")

    city_lower = city.lower()
    cache_key = f"{city_lower}-{start_date}-{days}"
    cached_weather = await weather_collection.find_one({"cache_key": cache_key})

    if cached_weather:
        last_updated = cached_weather.get("updated_at")
        if last_updated:
            if last_updated.tzinfo is None:
                last_updated = last_updated.replace(tzinfo=timezone.utc)
            if (datetime.now(timezone.utc) - last_updated) < timedelta(minutes=30):
                print(f"✅ Zwracam POGODĘ na {days} dni z BAZY DANYCH dla: {city}")
                return {"data": cached_weather["data"], "city": cached_weather["city"]}

    print(f"☁️ Pobieram i generuję prognozę POGODY dla: {city} na {days} dni")
    params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric", "lang": "pl"}
    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(WEATHER_URL, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Błąd API pogody")

    base_data = response.json()
    base_temp = base_data["main"]["temp"]
    city_name = base_data["name"]
    forecast = []
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")

    ikony = {"Jasne niebo": "☀️", "Lekkie opady deszczu": "🌦️", "Pochmurno": "☁️", "Częściowe zachmurzenie": "⛅"}
    opisy = ["Jasne niebo", "Lekkie opady deszczu", "Pochmurno", "Częściowe zachmurzenie", "Jasne niebo"]

    for i in range(days):
        current_date = start_dt + timedelta(days=i)
        daily_temp = round(base_temp + random.uniform(-3.0, 3.0), 1)
        desc = random.choice(opisy)

        forecast.append({
            "date": current_date.strftime("%d.%m"),
            "temperature": daily_temp,
            "description": desc,
            "icon": ikony.get(desc, "🌤️")
        })

    weather_data = {
        "cache_key": cache_key,
        "city": city_name,
        "data": forecast,
        "updated_at": datetime.now(timezone.utc)
    }
    await weather_collection.update_one({"cache_key": cache_key}, {"$set": weather_data}, upsert=True)

    return {"data": forecast, "city": city_name}

GEOAPIFY_KEY = os.getenv("GEOAPIFY_KEY")
TICKETMASTER_KEY = os.getenv("TICKETMASTER_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

pois_collection = db.pois_cache
events_collection = db.events_cache
itinerary_collection = db.itinerary_cache
@app.get("/api/pois")
async def get_pois(lat: float, lon: float):
    cache_key = f"{lat}-{lon}"
    cached_pois = await pois_collection.find_one({"cache_key": cache_key})

    if cached_pois and (
            datetime.now(timezone.utc) - cached_pois["updated_at"].replace(tzinfo=timezone.utc)) < timedelta(days=7):
        return {"data": cached_pois["data"]}

    print(f"📍 Szukam atrakcji (Geoapify) dla kordynatów: {lat}, {lon}")
    parsed_pois = []

    try:
        url = f"https://api.geoapify.com/v2/places?categories=tourism.sights,tourism.attraction&filter=circle:{lon},{lat},5000&limit=5&apiKey={GEOAPIFY_KEY}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                features = resp.json().get("features", [])
                for f in features:
                    props = f.get("properties", {})
                    parsed_pois.append({
                        "name": props.get("name", "Atrakcja turystyczna"),
                        "lat": props.get("lat"),
                        "lon": props.get("lon")
                    })
    except Exception as e:
        print(f"⚠️ Błąd Geoapify: {e}")

    await pois_collection.update_one(
        {"cache_key": cache_key},
        {"$set": {"cache_key": cache_key, "data": parsed_pois, "updated_at": datetime.now(timezone.utc)}},
        upsert=True
    )
    return {"data": parsed_pois}

@app.get("/api/events")
async def get_events(city: str, start_date: str, end_date: str):
    cache_key = f"{city.lower()}-{start_date}-{end_date}"
    cached_events = await events_collection.find_one({"cache_key": cache_key})

    if cached_events and (
            datetime.now(timezone.utc) - cached_events["updated_at"].replace(tzinfo=timezone.utc)) < timedelta(
            hours=24):
        return {"data": cached_events["data"]}

    print(f"🎸 Szukam wydarzeń (Ticketmaster) w: {city} od {start_date} do {end_date}")
    parsed_events = []

    try:
        start_dt = f"{start_date}T00:00:00Z"
        end_dt = f"{end_date}T23:59:59Z"
        url = f"https://app.ticketmaster.com/discovery/v2/events.json?city={city}&startDateTime={start_dt}&endDateTime={end_dt}&apikey={TICKETMASTER_KEY}&size=4&sort=relevance,desc"

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                events_raw = resp.json().get("_embedded", {}).get("events", [])
                for e in events_raw:
                    parsed_events.append({
                        "name": e.get("name"),
                        "date": e.get("dates", {}).get("start", {}).get("localDate", "Brak daty"),
                        "url": e.get("url", "#"),
                        "image": e.get("images", [{"url": ""}])[0]["url"]
                    })
    except Exception as e:
        print(f"⚠️ Błąd Ticketmaster: {e}")
    if not parsed_events:
        parsed_events = [
            {"name": "Lokalny festiwal jedzenia (Wydarzenie przykładowe)", "date": start_date, "url": "#", "image": ""}]

    await events_collection.update_one(
        {"cache_key": cache_key},
        {"$set": {"cache_key": cache_key, "data": parsed_events, "updated_at": datetime.now(timezone.utc)}},
        upsert=True
    )
    return {"data": parsed_events}

@app.get("/api/itinerary")
async def get_itinerary(city: str, days: int):
    cache_key = f"{city.lower()}-{days}-ollama"
    cached_itinerary = await itinerary_collection.find_one({"cache_key": cache_key})
    if cached_itinerary and (
            datetime.now(timezone.utc) - cached_itinerary["updated_at"].replace(tzinfo=timezone.utc)) < timedelta(
        days=30):
        print("✅ Zwracam plan wycieczki z cache (Ollama)!")
        return {"data": cached_itinerary["data"]}

    print(f"🤖 Generuję plan wycieczki z LOKALNEJ Ollamy (llama3.1:8b) dla: {city} na {days} dni")

    prompt = f"Jesteś doświadczonym przewodnikiem turystycznym. Napisz krótki, inspirujący plan wycieczki do miasta {city} na {days} dni. Zwróć go jako kod HTML (użyj znaczników <h3> dla dni, <ul> i <li> dla punktów). Nie dodawaj znaczników ```html na początku, zwróć czysty kod HTML."

    itinerary_html = "<h3>Dzień 1: Odkrywanie miasta</h3><ul><li>Spacer po centrum</li><li>Lokalna kolacja</li></ul>"

    try:
        ollama_url = "http://localhost:11434/api/generate"
        payload = {
            "model": "llama3.1:8b",
            "prompt": prompt,
            "stream": False
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(ollama_url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                itinerary_html = data.get("response", itinerary_html)
            else:
                print(f"⚠️ Błąd Ollamy: {resp.status_code}")

    except httpx.ConnectError:
        print("⚠️ Nie można połączyć się z Ollamą (Plan wycieczki).")
        itinerary_html = "<h3 class='text-error'>Błąd: Nie można połączyć się z lokalnym serwerem Ollama. Upewnij się, że jest włączony.</h3>"
    except Exception as e:
        print(f"⚠️ Błąd połączenia z Ollamą (Plan wycieczki): {e}")

    await itinerary_collection.update_one(
        {"cache_key": cache_key},
        {"$set": {"cache_key": cache_key, "data": itinerary_html, "updated_at": datetime.now(timezone.utc)}},
        upsert=True
    )
    return {"data": itinerary_html}


class ChatMessage(BaseModel):
    message: str
    city: str


@app.post("/api/chat")
async def chat_with_ollama(request: ChatMessage):
    print(f"🦙 Zapytanie do lokalnego Ollama (Llama 3.1:8b) o miasto {request.city}...")

    ollama_url = "http://localhost:11434/api/generate"
    prompt = f"Jesteś przyjaznym i zwięzłym asystentem podróży. Użytkownik planuje wycieczkę do miasta {request.city}. Odpowiedz krótko, naturalnie i po polsku na jego pytanie: {request.message}"

    payload = {
        "model": "llama3.1:8b",
        "prompt": prompt,
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(ollama_url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return {"reply": data.get("response", "Brak odpowiedzi od modelu.")}
            else:
                return {"reply": f"Błąd Ollamy: {resp.status_code}"}
    except httpx.ConnectError:
        return {
            "reply": "⚠️ Nie można połączyć się z Ollamą. Upewnij się, że serwer lokalny działa (uruchom 'ollama run llama3.1:8b' w konsoli)."}
    except Exception as e:
        print(f"⚠️ Błąd: {e}")
        return {"reply": "Wystąpił problem z asystentem."}