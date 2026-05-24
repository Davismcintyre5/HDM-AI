import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def promote():
    client = AsyncIOMotorClient("mongodb+srv://restomanager_admin:Hdm%402002@cluster0.i5j7cns.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client.hdm_ai_general
    result = await db.users.update_one(
        {"email": "davismcintyre5@gmail.com", "role": "user"},
        {"$set": {"role": "admin"}}
    )
    if result.modified_count:
        print("Promoted to admin")
    else:
        print("User not found or already admin")

asyncio.run(promote())