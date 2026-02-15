import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.services import user as user_service
from app.schemas.auth import UserCreate

async def seed_test_user():
    async with AsyncSessionLocal() as db:
        user = await user_service.get_user_by_email(db, email="test@xether.ai")
        if not user:
            user_in = UserCreate(
                email="test@xether.ai",
                password="testpassword123"
            )
            await user_service.create_user(db, user_in=user_in)
            print("Test user created.")
        else:
            print("Test user already exists.")

if __name__ == "__main__":
    asyncio.run(seed_test_user())
