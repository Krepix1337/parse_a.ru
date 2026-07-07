from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

if settings.MODE == "TEST":
    DATABASE_URL = settings.TEST_DATABASE_URL
else:
    DATABASE_URL = settings.DATABASE_URL

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
)

async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    async with async_session_maker() as session:
        yield session


class Base(DeclarativeBase):
    pass