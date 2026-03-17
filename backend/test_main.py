import pytest
from httpx import AsyncClient
from httpx import ASGITransport
import motor.motor_asyncio
from main import app, client as mongo_client

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
async def setup_db():
    """Przed testami zmieniamy referencje do bazy, by nie pisać po produkcyjnej"""
    from main import db, weather_collection, hotels_collection, flights_collection
    test_db = mongo_client.travel_planner_test
    await test_db.weather_cache.delete_many({})
    await test_db.hotels_cache.delete_many({})
    await test_db.flights_cache.delete_many({})
    await db.weather_cache.delete_many({})
    await db.hotels_cache.delete_many({})

    yield
    await db.weather_cache.delete_many({})
    await db.hotels_cache.delete_many({})


async def test_read_root():
    """Test sprawdza, czy główny endpoint odpowiada i serwer żyje."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Backend działa! Witaj w Smart Travel Planner."}


async def test_get_weather():
    """Test sprawdza, czy logika pogodowa (i fallback) poprawnie generuje 3 dni prognozy."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/weather/Warsaw?start_date=2026-05-20&days=3")
    assert response.status_code == 200
    data = response.json()
    assert "city" in data
    assert "data" in data
    assert len(data["data"]) == 3
    first_day = data["data"][0]
    assert "temperature" in first_day
    assert "description" in first_day
    assert "icon" in first_day


async def test_fallback_hotels():
    """Test sprawdza, czy w przypadku braku hoteli, mechanizm awaryjny generuje 4 losowe obiekty."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/hotels?city=Nibylandia&check_in=2026-10-10&check_out=2026-10-15")
    assert response.status_code == 200
    data = response.json()

    assert "data" in data
    assert len(data["data"]) == 4

    assert "Nibylandia" in data["data"][0]["name"]