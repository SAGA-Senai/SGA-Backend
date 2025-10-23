# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgresql://") and "+asyncpg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

if DATABASE_URL and "sslmode" in DATABASE_URL:
    from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
    parsed = urlparse(DATABASE_URL)
    query_params = parse_qs(parsed.query)
    query_params.pop('sslmode', None)
    new_query = urlencode(query_params, doseq=True)
    DATABASE_URL = urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment
    ))

if DATABASE_URL:
    engine = create_async_engine(DATABASE_URL, echo=True)
else:
    print("⚠️  AVISO: DATABASE_URL não configurada. Configure no arquivo .env")
    print("Exemplo: DATABASE_URL=postgresql+asyncpg://usuario:senha@localhost/database")
    engine = None
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# ✅ CORRETO
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
