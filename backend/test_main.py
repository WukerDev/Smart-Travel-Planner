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

