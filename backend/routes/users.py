"""
Kullanıcı API endpoint'leri
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Dict, Any

from backend.src.db_pg import get_db
from backend.src.models_pg import User, Interaction

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("")
async def get_all_users(db: AsyncSession = Depends(get_db)) -> List[Dict[str, Any]]:
    """Tüm kullanıcıları getir"""
    try:
        result = await db.execute(select(User))
        users = result.scalars().all()
        return [{"_id": str(u.id), **u.__dict__} for u in users]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kullanıcılar getirilirken hata: {str(e)}")


@router.get("/{user_id}")
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Belirli bir kullanıcıyı getir"""
    try:
        result = await db.execute(select(User).where(User.user_id == user_id))
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(status_code=404, detail=f"Kullanıcı bulunamadı: {user_id}")
        
        return {"_id": str(user.id), **user.__dict__}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Kullanıcı getirilirken hata: {str(e)}")


@router.post("/auth/register")
async def register_user(user_data: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    """Yeni kullanıcı oluştur (Benzersiz email ve şifre ile)"""
    try:
        email = user_data.get("email")
        password = user_data.get("password")
        
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email ve şifre zorunludur.")
        
        # Email kontrolü
        result = await db.execute(select(User).where(User.email == email))
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Bu email adresi zaten kullanımda.")
            
        # Yeni user_id oluştur
        result = await db.execute(select(User).order_by(User.user_id.desc()).limit(1))
        last_user = result.scalars().first()
        new_id = (last_user.user_id + 1) if last_user and last_user.user_id else 1
        
        new_user = User(
            user_id=new_id,
            full_name=user_data.get("full_name"),
            email=email,
            password=password, # Gerçek projede hash'lenmeli
            selected_genres=user_data.get("selected_genres", [])
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # Interaction tablosuna başlangıç kaydı - Sadece postgres id değil interaction_id ile
        new_int = Interaction(
            interaction_id=new_id * 1000,
            user_id=new_id,
            movie_id=0,
            is_liked=False,
            rating=0.0
        )
        db.add(new_int)
        await db.commit()
        
        # Şifreyi dönme
        user_dict = new_user.__dict__.copy()
        user_dict.pop("password", None)
        return {"status": "success", "user_id": new_id, "user": {"_id": str(new_user.id), **user_dict}}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Kayıt sırasında hata: {str(e)}")


@router.post("/auth/login")
async def login_user(login_data: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    """Email ve şifre ile giriş yap"""
    try:
        email = login_data.get("email")
        password = login_data.get("password")
        
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        
        if not user or user.password != password:
            raise HTTPException(status_code=401, detail="Email veya şifre hatalı.")
            
        user_dict = user.__dict__.copy()
        user_dict.pop("password", None)
        return {"status": "success", "user": {"_id": str(user.id), **user_dict}}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Giriş sırasında hata: {str(e)}")


@router.post("/{user_id}/preferences")
async def save_user_preferences(user_id: int, preferences: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    """Kullanıcının seçtiği türleri kaydet"""
    try:
        selected_genres = preferences.get("selected_genres", [])
        
        # Users tablosunu güncelle
        result = await db.execute(select(User).where(User.user_id == user_id))
        user = result.scalars().first()
        if user:
            user.selected_genres = selected_genres
            
        await db.commit()
            
        return {"status": "success", "message": "Tercihler kaydedildi"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Tercihler kaydedilirken hata: {str(e)}")
