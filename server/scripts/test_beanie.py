# ====================================================================================================
# server/test_beanie.py
# ====================================================================================================
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie, Document

class TestDoc(Document):
    name: str
    class Settings:
        name = "test_collection"

async def test():
    try:
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        await init_beanie(database=client.test_beanie_db, document_models=[TestDoc])
        print("Beanie: OK")
    except Exception as e:
        print(f"Beanie: FAILED - {e}")

asyncio.run(test())