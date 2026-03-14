import os
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from dotenv import load_dotenv
import motor.motor_asyncio

load_dotenv()

app = FastAPI(title="Smart Travel Planner API")

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


@app.get("/")
async def root():
    return {"message": "Backend działa! Witaj w Smart Travel Planner."}


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
                print("✅ Zwracam HOTELE z bazy danych (Cache)!")
                return {"data": cached_hotels["data"]}

    print(f"🏨 Szukam hoteli dla: {city} ({check_in} do {check_out})")

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "TWOJ_HOST_BOOKING_Z_RAPIDAPI"
    }

    async with httpx.AsyncClient() as client:

        parsed_hotels = [
            {"name": "Przykładowy Hotel Centrum", "rating": 8.5, "price": 450, "currency": "PLN"},
            {"name": "Apartamenty Stare Miasto", "rating": 9.2, "price": 320, "currency": "PLN"}
        ]

    await hotels_collection.update_one(
        {"cache_key": cache_key},
        {
            "$set": {
                "cache_key": cache_key,
                "data": parsed_hotels,
                "updated_at": datetime.now(timezone.utc)
            }
        },
        upsert=True
    )

    return {"data": parsed_hotels}

flights_collection = db.flights_cache
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")


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
                print("✅ Zwracam LOTY z bazy danych (Cache)!")
                return {"data": cached_flights["data"]}

    print(f"✈️ Szukam lotów w RapidAPI dla: {origin} -> {destination} na {date}")

    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": "sky-scrapper.p.rapidapi.com"
    }
    async with httpx.AsyncClient() as client:

        orig_resp = await client.get(
            "https://sky-scrapper.p.rapidapi.com/api/v1/flights/searchAirport",
            headers=headers, params={"query": origin}
        )
        orig_data = orig_resp.json().get("data", [])
        if not orig_data:
            raise HTTPException(status_code=404, detail=f"Nie znaleziono lotniska: {origin}")

        # Wyciągamy pierwsze trafienie z listy
        orig_sky_id = orig_data[0]["skyId"]
        orig_entity_id = orig_data[0]["entityId"]

        dest_resp = await client.get(
            "https://sky-scrapper.p.rapidapi.com/api/v1/flights/searchAirport",
            headers=headers, params={"query": destination}
        )
        dest_data = dest_resp.json().get("data", [])
        if not dest_data:
            raise HTTPException(status_code=404, detail=f"Nie znaleziono lotniska: {destination}")

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
        flight_resp = await client.get(
            "https://sky-scrapper.p.rapidapi.com/api/v1/flights/searchFlights",
            headers=headers, params=flight_params
        )

        if flight_resp.status_code != 200:
            raise HTTPException(status_code=flight_resp.status_code, detail="Błąd pobierania lotów z RapidAPI.")

        raw_flights_data = flight_resp.json()
        try:
            itineraries = raw_flights_data["data"]["itineraries"]
        except KeyError:
            itineraries = []

        parsed_flights = []
        for it in itineraries[:5]:
            leg = it["legs"][0]
            parsed_flights.append({
                "id": it["id"],
                "airline": leg["carriers"]["marketing"][0]["name"] if leg["carriers"]["marketing"] else "Nieznana",
                "departure_time": leg["departure"].split("T")[1][:5],
                "arrival_time": leg["arrival"].split("T")[1][:5],
                "price": it["price"]["raw"]
            })

    await flights_collection.update_one(
        {"cache_key": cache_key},
        {
            "$set": {
                "cache_key": cache_key,
                "data": parsed_flights,
                "updated_at": datetime.now(timezone.utc)
            }
        },
        upsert=True
    )

    return {"data": parsed_flights}


@app.get("/api/weather/{city}")
async def get_weather(city: str):
    if not WEATHER_API_KEY:
        raise HTTPException(status_code=500, detail="Brak klucza API do pogody w pliku .env!")
    city_lower = city.lower()
    cached_weather = await weather_collection.find_one({"city_lower": city_lower})

    if cached_weather:
        last_updated = cached_weather.get("updated_at")
        if last_updated and (datetime.now(timezone.utc) - last_updated) < timedelta(minutes=30):
            print(f"✅ Zwracam dane z BAZY DANYCH dla: {city}")
            return {
                "city": cached_weather["city"],
                "temperature": cached_weather["temperature"],
                "description": cached_weather["description"],
                "humidity": cached_weather["humidity"],
                "wind_speed": cached_weather["wind_speed"],
                "source": "database"
            }

    print(f"☁️ Pobieram nowe dane z API dla: {city}")
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "pl"
    }

    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(WEATHER_URL, params=params)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Błąd API pogody: {response.text}"
        )

    data = response.json()
    weather_data = {
        "city": data["name"],
        "city_lower": city_lower,
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"].capitalize(),
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"],
        "updated_at": datetime.now(timezone.utc)
    }

    await weather_collection.update_one(
        {"city_lower": city_lower},
        {"$set": weather_data},
        upsert=True
    )

    response_data = {k: v for k, v in weather_data.items() if k not in ["city_lower", "updated_at"]}
    response_data["source"] = "api"

    return response_data