import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
from pathlib import Path

# .env dosyasını yükle (Yerel geliştirme için)
try:
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except Exception:
    pass

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Vercel'de DATABASE_URL bulunamazsa uygulama hata vermeden önce uyarı versin
    print("ERROR: DATABASE_URL environment variable is MISSING!")
    # Fallback to empty string to avoid crash during import, but will fail on connection
    DATABASE_URL = ""

# asyncpg uyumluluğu için postgresql://'i postgresql+asyncpg://'e çeviriyoruz
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

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
