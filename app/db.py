from collections.abc import AsyncGenerator
from datetime import datetime

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from settings import db_url

engine = create_async_engine(url=db_url, echo=True, poolclass=NullPool,)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())

