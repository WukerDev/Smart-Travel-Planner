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

# --- Konfiguracja MongoDB ---
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
db = client.travel_planner
weather_collection = db.weather_cache


@app.get("/")
async def root():
    return {"message": "Backend działa! Witaj w Smart Travel Planner."}


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