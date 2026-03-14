import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Smart Travel Planner API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], # Port Twojego Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

@app.get("/")
async def root():
    return {"message": "Backend działa! Witaj w Smart Travel Planner."}

@app.get("/api/weather/{city}")
async def get_weather(city: str):
    if not WEATHER_API_KEY:
        raise HTTPException(status_code=500, detail="Brak klucza API do pogody w pliku .env!")
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric",
        "lang": "pl"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(WEATHER_URL, params=params)
    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Nie udało się pobrać pogody. Sprawdź nazwę miasta."
        )
    data = response.json()
    return {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"].capitalize(),
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"]
    }