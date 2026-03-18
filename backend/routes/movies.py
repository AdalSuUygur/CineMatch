"""
Film API endpoint'leri
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, and_, desc, func, text
from typing import List, Optional, Dict, Any

from backend.src.db_pg import get_db
from backend.src.models_pg import Movie, MovieGenre

router = APIRouter(prefix="/api/movies", tags=["movies"])


@router.get("")
async def get_all_movies(
    skip: int = Query(0, ge=0, description="Atlanacak kayıt sayısı"),
    limit: int = Query(20, ge=1, le=100, description="Getirilecek kayıt sayısı"),
    search: Optional[str] = Query(None, description="Film adında arama"),
    genre_ids: Optional[str] = Query(None, description="Virgülle ayrılmış tür ID'leri"),
    sort_by: Optional[str] = Query(None, description="Sıralama kriteri (popularity gibi)"),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Tüm filmleri getir (pagination ve tür filtresi ile)"""
    try:
        stmt = select(Movie)
        
        # Temel arama filtresi
        if search:
            stmt = stmt.where(Movie.title.ilike(f"%{search}%"))
            
        # Tür filtresi ekle
        if genre_ids:
            genre_id_list = [int(gid.strip()) for gid in genre_ids.split(",") if gid.strip().isdigit()]
            if genre_id_list:
                movie_genre_stmt = select(MovieGenre.movie_id).where(MovieGenre.genre_id.in_(genre_id_list))
                movie_genres_result = await db.execute(movie_genre_stmt)
                movie_ids = list(set([row[0] for row in movie_genres_result.all()]))
                
                if movie_ids:
                    stmt = stmt.where(Movie.movieId.in_(movie_ids))
                    stmt = stmt.where(Movie.vote_average > 5.0)
                else:
                    return []

        # Sıralama: explicit sort_by=popularity için DESC, aksi hâlde yeni filmlere ağırlıklı rastgele
        if sort_by == "popularity":
            stmt = stmt.order_by(desc(Movie.popularity))
        else:
            # RANDOM() * year → yeni filmler daha yüksek istatistiksel skor alır ama eski filmler de çıkabilir
            stmt = stmt.order_by(text("RANDOM() * COALESCE(EXTRACT(YEAR FROM release_date), 1970) DESC"))
            
        # Pagination
        stmt = stmt.offset(skip).limit(limit)
        
        # Execute query
        result = await db.execute(stmt)
        movies = result.scalars().all()
        
        # Pydantic dict format
        return [{"_id": str(m.movieId), **{k: v for k, v in m.__dict__.items() if k != "_sa_instance_state"}} for m in movies]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filmler getirilirken hata: {str(e)}")


@router.get("/{movie_id}")
async def get_movie_by_id(movie_id: int, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Belirli bir filmi getir"""
    try:
        stmt = select(Movie).where(Movie.movieId == movie_id)
        result = await db.execute(stmt)
        movie = result.scalars().first()
        
        if not movie:
            raise HTTPException(status_code=404, detail=f"Film bulunamadı: {movie_id}")
        
        return {"_id": str(movie.movieId), **{k: v for k, v in movie.__dict__.items() if k != "_sa_instance_state"}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Film getirilirken hata: {str(e)}")


@router.get("/search/query")
async def search_movies(
    q: str = Query(..., min_length=1, description="Arama terimi"),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Film ara"""
    try:
        stmt = select(Movie).where(
            or_(
                Movie.title.ilike(f"%{q}%"),
                Movie.original_title.ilike(f"%{q}%")
            )
        ).limit(50)
        
        result = await db.execute(stmt)
        movies = result.scalars().all()
        
        return [{"_id": str(m.movieId), **{k: v for k, v in m.__dict__.items() if k != "_sa_instance_state"}} for m in movies]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Arama yapılırken hata: {str(e)}")
