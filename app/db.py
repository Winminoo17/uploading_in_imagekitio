from collections.abc import AsyncIterator
import uuid

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, inspect, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.dialects.postgresql import UUID
import datetime
from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID

load_dotenv()
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

class Base(DeclarativeBase):
    pass

class User(SQLAlchemyBaseUserTableUUID, Base):
    posts = relationship("Post", back_populates="user")

class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    caption = Column(Text)
    url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    user = relationship("User", back_populates="posts")


engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_migrate_posts_table)


def _migrate_posts_table(connection):
    post_columns = {column["name"] for column in inspect(connection).get_columns("posts")}
    if "user_id" not in post_columns:
        connection.execute(
            text("ALTER TABLE posts ADD COLUMN user_id CHAR(36) REFERENCES user(id)")
        )
        connection.execute(
            text(
                "UPDATE posts SET user_id = "
                "(SELECT id FROM user ORDER BY rowid LIMIT 1) "
                "WHERE user_id IS NULL"
            )
        )

async def get_session() -> AsyncIterator[AsyncSession, None]:
    async with async_session() as session:
        yield session

async def get_user_db(session : AsyncSession = Depends(get_session)):
    yield SQLAlchemyUserDatabase(session, User)