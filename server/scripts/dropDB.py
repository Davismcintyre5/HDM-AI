# ====================================================================================================
# server/scripts/dropDB.py
# ====================================================================================================
"""
HDM AI - Database Management Script
Drop collections, entire databases, or list all
Run: python scripts/dropDB.py
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from config import settings


DATABASES = [
    "hdm_ai_general",
    "hdm_ai_smartpos",
    "hdm_ai_spark",
    "hdm_ai_vibe",
    "hdm_ai_vault",
    "hdm_ai_erp",
    "hdm_ai_widget",
]


async def get_client():
    """Get MongoDB client."""
    return AsyncIOMotorClient(settings.MONGODB_URL)


async def list_all():
    """List all databases and their collections."""
    client = await get_client()
    
    print("\n" + "=" * 70)
    print("  HDM AI — ALL DATABASES & COLLECTIONS")
    print("=" * 70)
    
    for db_name in DATABASES:
        db = client[db_name]
        collections = await db.list_collection_names()
        
        print(f"\n  📁 {db_name}")
        if collections:
            for col in collections:
                count = await db[col].count_documents({})
                print(f"     └── {col} ({count} documents)")
        else:
            print("     └── (empty)")
    
    print("\n" + "=" * 70)


async def list_collections():
    """List collections for a specific database."""
    print("\n" + "=" * 70)
    print("  SELECT DATABASE")
    print("=" * 70)
    
    for i, db_name in enumerate(DATABASES, 1):
        print(f"  {i}. {db_name}")
    print(f"  {len(DATABASES) + 1}. All databases")
    print("  0. Cancel")
    
    choice = input("\n  Choose: ").strip()
    
    if choice == "0":
        return
    
    client = await get_client()
    
    if choice == str(len(DATABASES) + 1):
        await list_all()
        return
    
    try:
        idx = int(choice) - 1
        db_name = DATABASES[idx]
    except (ValueError, IndexError):
        print("  ✗ Invalid choice.")
        return
    
    db = client[db_name]
    collections = await db.list_collection_names()
    
    print(f"\n  📁 {db_name}")
    print("  " + "-" * 50)
    
    if not collections:
        print("  (empty)")
        return
    
    for col in collections:
        count = await db[col].count_documents({})
        indexes = await db[col].index_information()
        print(f"\n  📄 {col}")
        print(f"     Documents: {count}")
        print(f"     Indexes: {len(indexes)}")


async def drop_collections():
    """Drop specific collections from a database."""
    print("\n" + "=" * 70)
    print("  DROP COLLECTIONS")
    print("=" * 70)
    
    for i, db_name in enumerate(DATABASES, 1):
        print(f"  {i}. {db_name}")
    print("  0. Cancel")
    
    choice = input("\n  Choose database: ").strip()
    
    if choice == "0":
        return
    
    try:
        idx = int(choice) - 1
        db_name = DATABASES[idx]
    except (ValueError, IndexError):
        print("  ✗ Invalid choice.")
        return
    
    client = await get_client()
    db = client[db_name]
    collections = await db.list_collection_names()
    
    if not collections:
        print(f"\n  Database '{db_name}' is empty.")
        return
    
    print(f"\n  Collections in {db_name}:")
    for i, col in enumerate(collections, 1):
        count = await db[col].count_documents({})
        print(f"  {i}. {col} ({count} documents)")
    
    print("\n  Options:")
    print("  - Enter collection numbers separated by commas (e.g., 1,3,5)")
    print("  - Type 'all' to drop ALL collections in this database")
    print("  - Type '0' to cancel")
    
    choice = input("\n  Choose: ").strip()
    
    if choice == "0":
        return
    
    if choice.lower() == "all":
        confirm = input(f"\n  ⚠️  Drop ALL collections in '{db_name}'? Type 'YES': ").strip()
        if confirm != "YES":
            print("  Cancelled.")
            return
        
        for col in collections:
            await db[col].drop()
            print(f"  ✓ Dropped: {col}")
        
        print(f"\n  ✓ All collections dropped from '{db_name}'.")
        return
    
    try:
        indices = [int(x.strip()) - 1 for x in choice.split(",")]
    except ValueError:
        print("  ✗ Invalid input.")
        return
    
    selected = [collections[i] for i in indices if 0 <= i < len(collections)]
    
    if not selected:
        print("  ✗ No valid collections selected.")
        return
    
    print(f"\n  ⚠️  You are about to drop:")
    for col in selected:
        count = await db[col].count_documents({})
        print(f"     - {col} ({count} documents)")
    
    confirm = input("\n  Type 'DROP' to confirm: ").strip()
    
    if confirm != "DROP":
        print("  Cancelled.")
        return
    
    for col in selected:
        await db[col].drop()
        print(f"  ✓ Dropped: {col}")
    
    print(f"\n  ✓ {len(selected)} collection(s) dropped.")


async def drop_database():
    """Drop an entire database."""
    print("\n" + "=" * 70)
    print("  DROP ENTIRE DATABASE")
    print("=" * 70)
    print("\n  ⚠️  WARNING: This permanently deletes ALL data in the database!")
    
    for i, db_name in enumerate(DATABASES, 1):
        print(f"  {i}. {db_name}")
    print(f"  {len(DATABASES) + 1}. DROP ALL 7 DATABASES")
    print("  0. Cancel")
    
    choice = input("\n  Choose: ").strip()
    
    if choice == "0":
        return
    
    client = await get_client()
    
    if choice == str(len(DATABASES) + 1):
        print("\n  ⚠️  You are about to DROP ALL 7 HDM AI databases!")
        print("  This will delete EVERYTHING — users, keys, conversations, all data.")
        confirm = input("\n  Type 'DELETE EVERYTHING' to confirm: ").strip()
        
        if confirm != "DELETE EVERYTHING":
            print("  Cancelled.")
            return
        
        for db_name in DATABASES:
            await client.drop_database(db_name)
            print(f"  ✓ Dropped: {db_name}")
        
        print("\n  ✓ All 7 databases dropped. HDM AI is now empty.")
        return
    
    try:
        idx = int(choice) - 1
        db_name = DATABASES[idx]
    except (ValueError, IndexError):
        print("  ✗ Invalid choice.")
        return
    
    # Count total documents
    db = client[db_name]
    total_docs = 0
    for col in await db.list_collection_names():
        total_docs += await db[col].count_documents({})
    
    print(f"\n  ⚠️  About to drop: {db_name}")
    print(f"     Total documents: {total_docs}")
    
    confirm = input(f"\n  Type '{db_name}' to confirm: ").strip()
    
    if confirm != db_name:
        print("  Cancelled.")
        return
    
    await client.drop_database(db_name)
    print(f"\n  ✓ Database '{db_name}' permanently dropped.")


async def main():
    """Main interactive loop."""
    while True:
        print("\n" + "=" * 70)
        print("  HDM AI — DATABASE MANAGER")
        print("=" * 70)
        print("\n  1. List all databases & collections")
        print("  2. List collections (specific database)")
        print("  3. Drop collections")
        print("  4. Drop entire database")
        print("  5. Exit")
        
        choice = input("\n  Choose (1-5): ").strip()
        
        if choice == "1":
            await list_all()
        elif choice == "2":
            await list_collections()
        elif choice == "3":
            await drop_collections()
        elif choice == "4":
            await drop_database()
        elif choice == "5":
            print("\n  Goodbye.")
            break
        else:
            print("\n  ✗ Invalid choice.")
        
        input("\n  Press Enter to continue...")


if __name__ == "__main__":
    asyncio.run(main())