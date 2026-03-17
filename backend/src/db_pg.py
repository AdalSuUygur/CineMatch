import os
from sqlalchemy import text
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

# asyncpg, sslmode ve channel_binding gibi parametreleri query string'de desteklemez.
# Bu parametreleri temizleyelim ve Neon için gerekli olan SSL ayarını düzgün yapalım.
connect_args = {}
if "?" in DATABASE_URL:
    base_url, query = DATABASE_URL.split("?", 1)
    import urllib.parse
    params = urllib.parse.parse_qs(query)
    
    # sslmode=require varsa veya Neon hostuysa SSL'i zorunlu tutalım
    is_neon = "neon.tech" in base_url
    if 'sslmode' in params or is_neon:
        connect_args["ssl"] = "require"
    
    # asyncpg için sorun çıkaranları temizle
    params.pop('sslmode', None)
    params.pop('channel_binding', None)
    
    new_query = urllib.parse.urlencode(params, doseq=True)
    DATABASE_URL = f"{base_url}?{new_query}" if new_query else base_url
elif "neon.tech" in DATABASE_URL:
    connect_args["ssl"] = "require"

engine = create_async_engine(DATABASE_URL, echo=False, connect_args=connect_args)

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
    """Veritabanı bağlantısını doğrula"""
    # Gerekli modelleri içe aktar (Metadata kaydı için gerekebilir)
    import backend.src.models_pg
    try:
        async with engine.begin() as conn:
            # Sadece bağlantıyı test et, tablo oluşturma işlemini kullanıcı manuel yapmış varsayıyoruz.
            # Eğer tablolar yoksa ve oluşturulması gerekiyorsa aşağıdaki satır yorumdan çıkarılabilir:
            # await conn.run_sync(Base.metadata.create_all)
            await conn.execute(text("SELECT 1"))
        print("PostgreSQL bağlantısı doğrulandı.")
    except Exception as e:
        print(f"PostgreSQL bağlantı hatası: {e}")

async def close_db():
    await engine.dispose()
    print("PostgreSQL bağlantısı kapatıldı.")
