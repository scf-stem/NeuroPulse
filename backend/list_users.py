
import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User

async def list_users():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User))
        users = result.scalars().all()
        print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Active':<10}")
        print("-" * 70)
        for user in users:
            print(f"{user.id:<5} {user.username:<20} {user.email:<30} {user.is_active:<10}")

if __name__ == "__main__":
    asyncio.run(list_users())
