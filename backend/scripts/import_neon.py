import asyncio
import pandas as pd
import os
import sys
from pathlib import Path
from sqlalchemy.future import select
from sqlalchemy import text

# Proje kök dizinini sys.path'e ekle
root_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_path))

from backend.src.db_pg import engine, init_db, async_session_maker
from backend.src.models_pg import Movie, Genre, MovieGenre

DATA_DIR = root_path / "backend" / "data"

async def import_genres():
    print("Türler (Genres) aktarılıyor...")
    df = pd.read_csv(DATA_DIR / "genres.csv")
    async with async_session_maker() as session:
        for _, row in df.iterrows():
            genre = Genre(
                genre_id=int(row['genre_id']),
                genre_name=row['genre_name']
            )
            session.add(genre)
        await session.commit()
    print(f"{len(df)} tür başarıyla aktarıldı.")

async def import_movies():
    print("Filmler (Movies) aktarılıyor... (Bu biraz zaman alabilir)")
    df = pd.read_csv(DATA_DIR / "movies_with_metadata.csv")
    # NaN değerleri temizle
    df = df.where(pd.notnull(df), None)
    
    async with async_session_maker() as session:
        count = 0
        for _, row in df.iterrows():
            movie = Movie(
                movieId=int(row['movie_id']),
                title=row['title'],
                imdbId=str(row['imdbid']) if row['imdbid'] else None,
                tmdbId=int(row['tmdbid']) if row['tmdbid'] else None,
                original_language=row['original_language'],
                original_title=row['original_title'],
                popularity=float(row['popularity']) if row['popularity'] else 0.0,
                release_date=str(row['release_date']) if row['release_date'] else None,
                vote_average=float(row['vote_average']) if row['vote_average'] else 0.0,
                poster_url=row['poster_url'],
                llm_metadata=row['llm_metadata']
            )
            session.add(movie)
            count += 1
            if count % 100 == 0:
                await session.flush()
                print(f"{count} film hazırlandı...")
        
        await session.commit()
    print(f"{len(df)} film başarıyla aktarıldı.")

async def import_movie_genres():
    print("Film-Tür ilişkileri aktarılıyor...")
    df = pd.read_csv(DATA_DIR / "movie_genres.csv")
    async with async_session_maker() as session:
        count = 0
        for _, row in df.iterrows():
            rel = MovieGenre(
                movie_id=int(row['movieId']),
                genre_id=int(row['genre_id'])
            )
            session.add(rel)
            count += 1
            if count % 1000 == 0:
                await session.flush()
                print(f"{count} ilişki hazırlandı...")
        await session.commit()
    print(f"{len(df)} ilişki başarıyla aktarıldı.")

async def main():
    print("Veri aktarımı başlatılıyor...")
    # Önce tabloları oluştur
    await init_db()
    
    # Sırayla aktar
    try:
        await import_genres()
    except Exception as e:
        print(f"Tür aktarımı hatası (Zaten var olabilir): {e}")
        
    try:
        await import_movies()
    except Exception as e:
        print(f"Film aktarımı hatası (Zaten var olabilir): {e}")

    try:
        await import_movie_genres()
    except Exception as e:
        print(f"Film-Tür aktarımı hatası (Zaten var olabilir): {e}")
        
    print("İşlem tamamlandı!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
