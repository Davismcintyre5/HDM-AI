import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def fix():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client.hdm_ai_general
    
    # Show current indexes
    indexes = await db.users.index_information()
    print("Current indexes:", list(indexes.keys()))
    
    # Drop the old unique email index
    try:
        await db.users.drop_index('email_1')
        print("Dropped: email_1")
    except Exception as e:
        print(f"Could not drop email_1: {e}")
    
    # Show updated indexes
    indexes = await db.users.index_information()
    print("Updated indexes:", list(indexes.keys()))

asyncio.run(fix())