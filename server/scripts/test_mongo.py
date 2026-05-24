import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test():
    try:
        client = AsyncIOMotorClient("mongodb://localhost:27017", serverSelectionTimeoutMS=5000)
        await client.admin.command("ping")
        print("MongoDB: CONNECTED")
    except Exception as e:
        print(f"MongoDB: FAILED - {e}")

asyncio.run(test())