import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
from pathlib import Path

# .env dosyasını yükle (Root dizininden)
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")

# asyncpg uyumluluğu için postgresql://'i postgresql+asyncpg://'e çeviriyoruz
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# fix for asyncpg url params
if DATABASE_URL:
    if "sslmode=" in DATABASE_URL:
        # replace sslmode=xxx with ssl=require for asyncpg
        import re
        DATABASE_URL = re.sub(r"sslmode=[^&?]+", "ssl=require", DATABASE_URL)
    elif "?" not in DATABASE_URL:
        DATABASE_URL += "?ssl=require"
    elif "ssl=" not in DATABASE_URL:
        DATABASE_URL += "&ssl=require"

engine = create_async_engine(DATABASE_URL, echo=False)

# Session factory
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    """Dependency for getting async session"""
    async with async_session_maker() as session:
        yield session

async def init_db():
    """Veritabanı tablolarını oluştur"""
    # Gerekli modelleri içe aktar
    import backend.src.models_pg
    async with engine.begin() as conn:
        # Uyarı: Prod ortamında otomatik tablo oluşturucu yerine Alembic (migration aracı) önerilir
        await conn.run_sync(Base.metadata.create_all)
    print("PostgreSQL veritabanı tabloları kontrol edildi/oluşturuldu.")

async def close_db():
    await engine.dispose()
    print("PostgreSQL bağlantısı kapatıldı.")
