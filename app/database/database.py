from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

db_url = settings.TEST_DATABASE_URL if settings.MODE == "TEST" else settings.DATABASE_URL

engine = create_async_engine(
    db_url,
    echo=(settings.MODE == "DEV"),
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