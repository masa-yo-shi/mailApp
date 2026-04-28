import os
from sqlalchemy.ext.asyncio import create_async_engine
from models.mail import Base
import asyncio

# create DBfile
base_dir = os.path.dirname(__file__)
DATABASE_URL = f"sqlite+aiosqlite:///{os.path.join(base_dir, 'mail.sqlite')}"

engine = create_async_engine(DATABASE_URL, echo=True)

# innitialize the database
async def init_db():
    print("Initializing the database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())