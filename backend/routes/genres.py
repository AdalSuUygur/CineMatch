"""
Tür (Genre) API endpoint'leri
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any

from backend.src.db_pg import get_db
from backend.src.models_pg import Genre, MovieGenre

router = APIRouter(prefix="/api/genres", tags=["genres"])


@router.get("")
async def get_all_genres(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """Tüm türleri getir"""
    try:
        result = await db.execute(select(Genre))
        genres = result.scalars().all()
        return [{"_id": str(g.genre_id), **g.__dict__} for g in genres]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Türler getirilirken hata: {str(e)}")


@router.get("/movie/{movie_id}")
async def get_movie_genres(movie_id: int, db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """Belirli bir filmin türlerini getir"""
    try:
        # Önce film-tür ilişkilerini al
        stmt = select(MovieGenre).where(MovieGenre.movie_id == movie_id)
        result = await db.execute(stmt)
        movie_genre_relations = result.scalars().all()
        
        if not movie_genre_relations:
            return []
        
        # Tür ID'lerini topla
        genre_ids = [relation.genre_id for relation in movie_genre_relations]
        
        # Türleri getir
        stmt_g = select(Genre).where(Genre.genre_id.in_(genre_ids))
        result_g = await db.execute(stmt_g)
        genres = result_g.scalars().all()
        
        return [{"_id": str(g.genre_id), **g.__dict__} for g in genres]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Film türleri getirilirken hata: {str(e)}")
