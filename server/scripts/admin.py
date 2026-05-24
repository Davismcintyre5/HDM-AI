# ====================================================================================================
# server/scripts/admin.py
# ====================================================================================================
"""
HDM AI - Admin Management CLI
Manage admin accounts only: create, list, promote, demote, activate, deactivate, delete
Run: python scripts/admin.py
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime
from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_db():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    return client.hdm_ai_general


async def list_admins():
    """List all admin accounts."""
    db = await get_db()
    admins = await db.users.find({"role": "admin"}).to_list(None)

    print("\n" + "=" * 60)
    print("  ADMIN ACCOUNTS")
    print("=" * 60)

    if not admins:
        print("  No admin accounts found.")
        return

    for i, a in enumerate(admins, 1):
        active = "✓ Active" if a.get("is_active", True) else "✗ Inactive"
        last = a.get("last_login")
        last_str = last.strftime("%Y-%m-%d %H:%M") if last else "Never"
        print(f"\n  [{i}] {a.get('email')}")
        print(f"      Username:   {a.get('username')}")
        print(f"      Status:     {active}")
        print(f"      Last Login: {last_str}")
        print(f"      Created:    {a.get('created_at')}")


async def create_admin():
    """Create a new admin account. Can share email with existing user account."""
    print("\n" + "=" * 60)
    print("  CREATE ADMIN")
    print("=" * 60)

    email = input("\n  Email: ").strip()
    username = input("  Username: ").strip()
    password = input("  Password: ").strip()

    if not email or not username or not password:
        print("\n  ✗ All fields required.")
        return
    if len(password) < 8:
        print("\n  ✗ Password must be at least 8 characters.")
        return

    db = await get_db()

    # Check existing admin only
    exists = await db.users.find_one({"email": email, "role": "admin"})
    if exists:
        print(f"\n  ✗ Admin '{email}' already exists.")
        return

    await db.users.insert_one({
        "email": email,
        "username": username,
        "hashed_password": pwd_context.hash(password[:72]),
        "role": "admin",
        "is_active": True,
        "created_at": datetime.utcnow(),
        "api_keys_count": 0,
        "total_requests": 0,
        "tokens_used": 0,
    })

    print(f"\n  ✓ Admin created: {email}")
    print(f"  Login: POST /api/v1/auth/admin/login")


async def activate_admin():
    """Activate a deactivated admin account."""
    print("\n" + "=" * 60)
    print("  ACTIVATE ADMIN")
    print("=" * 60)
    email = input("\n  Admin email: ").strip()

    db = await get_db()
    admin = await db.users.find_one({"email": email, "role": "admin"})
    if not admin:
        print(f"\n  ✗ Admin '{email}' not found.")
        return
    if admin.get("is_active"):
        print(f"\n  ✗ Admin '{email}' is already active.")
        return

    await db.users.update_one({"_id": admin["_id"]}, {"$set": {"is_active": True}})
    print(f"\n  ✓ Admin '{email}' activated.")


async def deactivate_admin():
    """Deactivate an admin account (prevents login)."""
    print("\n" + "=" * 60)
    print("  DEACTIVATE ADMIN")
    print("=" * 60)
    email = input("\n  Admin email: ").strip()

    db = await get_db()
    admin = await db.users.find_one({"email": email, "role": "admin"})
    if not admin:
        print(f"\n  ✗ Admin '{email}' not found.")
        return
    if not admin.get("is_active"):
        print(f"\n  ✗ Admin '{email}' is already inactive.")
        return

    # Prevent deactivating last active admin
    active_count = await db.users.count_documents({"role": "admin", "is_active": True})
    if active_count <= 1:
        print("\n  ✗ Cannot deactivate the last active admin.")
        print("     Create another admin first.")
        return

    await db.users.update_one({"_id": admin["_id"]}, {"$set": {"is_active": False}})
    print(f"\n  ✓ Admin '{email}' deactivated.")


async def delete_admin():
    """Permanently delete an admin account."""
    print("\n" + "=" * 60)
    print("  DELETE ADMIN")
    print("=" * 60)
    email = input("\n  Admin email to DELETE: ").strip()

    db = await get_db()
    admin = await db.users.find_one({"email": email, "role": "admin"})
    if not admin:
        print(f"\n  ✗ Admin '{email}' not found.")
        return

    # Prevent deleting last admin
    total_admins = await db.users.count_documents({"role": "admin"})
    if total_admins <= 1:
        print("\n  ✗ Cannot delete the last admin account.")
        print("     Create another admin first.")
        return

    print(f"\n  ⚠  Permanently delete admin: {admin.get('email')}")
    print(f"     Username: {admin.get('username')}")
    confirm = input("\n  Type 'DELETE' to confirm: ").strip()

    if confirm != "DELETE":
        print("  Cancelled.")
        return

    await db.users.delete_one({"_id": admin["_id"]})
    print(f"\n  ✓ Admin '{email}' permanently deleted.")


async def promote_to_admin():
    """Promote an existing user account to admin."""
    print("\n" + "=" * 60)
    print("  PROMOTE USER TO ADMIN")
    print("=" * 60)
    email = input("\n  User email to promote: ").strip()

    db = await get_db()
    user = await db.users.find_one({"email": email, "role": "user"})
    if not user:
        print(f"\n  ✗ User '{email}' not found. (They might already be admin or don't exist)")
        return

    print(f"\n  User: {user.get('email')} | {user.get('username')}")
    confirm = input("  Promote to admin? (y/n): ").strip().lower()

    if confirm != "y":
        print("  Cancelled.")
        return

    await db.users.update_one({"_id": user["_id"]}, {"$set": {"role": "admin"}})
    print(f"\n  ✓ '{email}' promoted to admin.")
    print(f"  They must now login at: POST /api/v1/auth/admin/login")


async def demote_to_user():
    """Demote an admin to regular user."""
    print("\n" + "=" * 60)
    print("  DEMOTE ADMIN TO USER")
    print("=" * 60)
    email = input("\n  Admin email to demote: ").strip()

    db = await get_db()
    admin = await db.users.find_one({"email": email, "role": "admin"})
    if not admin:
        print(f"\n  ✗ Admin '{email}' not found.")
        return

    total_admins = await db.users.count_documents({"role": "admin"})
    if total_admins <= 1:
        print("\n  ✗ Cannot demote the last admin.")
        return

    print(f"\n  Admin: {admin.get('email')} | {admin.get('username')}")
    confirm = input("  Demote to regular user? (y/n): ").strip().lower()

    if confirm != "y":
        print("  Cancelled.")
        return

    await db.users.update_one({"_id": admin["_id"]}, {"$set": {"role": "user"}})
    print(f"\n  ✓ '{email}' demoted to user.")
    print(f"  They must now login at: POST /api/v1/auth/login")


async def stats():
    """Show admin statistics."""
    db = await get_db()
    total = await db.users.count_documents({"role": "admin"})
    active = await db.users.count_documents({"role": "admin", "is_active": True})
    inactive = total - active

    print("\n" + "=" * 60)
    print("  ADMIN STATISTICS")
    print("=" * 60)
    print(f"\n  Total Admins:  {total}")
    print(f"  ├─ Active:     {active}")
    print(f"  └─ Inactive:   {inactive}")
    print(f"\n  Login: POST /api/v1/auth/admin/login")


async def main():
    while True:
        print("\n" + "=" * 60)
        print("  HDM AI — ADMIN MANAGEMENT")
        print("=" * 60)
        print("\n  1. List admins")
        print("  2. Create admin")
        print("  3. Activate admin")
        print("  4. Deactivate admin")
        print("  5. Delete admin")
        print("  6. Promote user → admin")
        print("  7. Demote admin → user")
        print("  8. Stats")
        print("  9. Exit")

        choice = input("\n  Choose (1-9): ").strip()

        if choice == "1":
            await list_admins()
        elif choice == "2":
            await create_admin()
        elif choice == "3":
            await activate_admin()
        elif choice == "4":
            await deactivate_admin()
        elif choice == "5":
            await delete_admin()
        elif choice == "6":
            await promote_to_admin()
        elif choice == "7":
            await demote_to_user()
        elif choice == "8":
            await stats()
        elif choice == "9":
            print("\n  Goodbye.")
            break
        else:
            print("\n  ✗ Invalid choice.")

        input("\n  Press Enter to continue...")


if __name__ == "__main__":
    asyncio.run(main())