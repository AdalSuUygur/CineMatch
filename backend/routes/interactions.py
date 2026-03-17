"""
Kullanıcı etkileşim API endpoint'leri
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from typing import List, Dict, Any

from backend.src.db_pg import get_db
from backend.src.models_pg import Interaction, User

router = APIRouter(prefix="/api/interactions", tags=["interactions"])


@router.get("")
async def get_all_interactions(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Tüm etkileşimleri getir (sayfalama ile)"""
    try:
        stmt = select(Interaction).offset(skip).limit(limit)
        result = await db.execute(stmt)
        interactions = result.scalars().all()
        return [{"_id": str(i.id), **{k: v for k, v in i.__dict__.items() if k != "_sa_instance_state"}} for i in interactions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Etkileşimler getirilirken hata: {str(e)}")


@router.get("/user/{user_id}")
async def get_user_interactions(
    user_id: int, 
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Belirli bir kullanıcının etkileşimlerini getir (sayfalama ile)"""
    try:
        stmt = select(Interaction).where(Interaction.user_id == user_id).offset(skip).limit(limit)
        result = await db.execute(stmt)
        interactions = result.scalars().all()
        return [{"_id": str(i.id), **{k: v for k, v in i.__dict__.items() if k != "_sa_instance_state"}} for i in interactions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kullanıcı etkileşimleri getirilirken hata: {str(e)}")


@router.post("")
async def create_interaction(data: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    """Yeni bir etkileşim kaydet veya güncelle"""
    try:
        user_id = data.get("user_id")
        movie_id = data.get("movie_id")
        
        # Varsa güncelle, yoksa oluştur
        stmt = select(Interaction).where(
            (Interaction.user_id == user_id) & (Interaction.movie_id == movie_id)
        )
        result = await db.execute(stmt)
        existing = result.scalars().first()
        
        if existing:
            if "is_liked" in data:
                existing.is_liked = data.get("is_liked")
            if "rating" in data:
                existing.rating = data.get("rating")
            
            await db.commit()
            return {"status": "updated"}
        else:
            # Yeni interaction_id oluştur
            result = await db.execute(select(Interaction).order_by(Interaction.interaction_id.desc()).limit(1))
            last_int = result.scalars().first()
            new_id = (last_int.interaction_id + 1) if last_int and last_int.interaction_id else 1001
            
            new_interaction = Interaction(
                interaction_id=new_id,
                user_id=user_id,
                movie_id=movie_id,
                is_liked=data.get("is_liked", False),
                rating=data.get("rating", 0.0)
            )
            
            db.add(new_interaction)
            await db.commit()
            return {"status": "created", "interaction_id": new_id}
            
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Etkileşim kaydedilirken hata: {str(e)}")


@router.delete("/user/{user_id}/movie/{movie_id}")
async def delete_interaction(user_id: int, movie_id: int, db: AsyncSession = Depends(get_db)):
    """Etkileşimi sil (Listeden çıkarma işlemi için)"""
    try:
        stmt = delete(Interaction).where(
            (Interaction.user_id == user_id) & (Interaction.movie_id == movie_id)
        )
        result = await db.execute(stmt)
        await db.commit()
        return {"status": "deleted", "count": result.rowcount}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Etkileşim silinirken hata: {str(e)}")
