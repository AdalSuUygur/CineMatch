from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.src.recommender import engine

router = APIRouter(prefix="/api/recommend", tags=["recommendations"])

class RecommendationRequest(BaseModel):
    user_id: Optional[int] = None
    selected_genres: Optional[List[int]] = []

@router.post("")
async def get_recommendations(request: RecommendationRequest):
    """
    Film önerilerini getir.
    Eğer user_id varsa kullanıcıya özel, yoksa seçilen türlere göre (guest) öneri yapar.
    """
    try:
        # Motorun hazır olduğundan emin ol (ilk istekte verileri yükler)
        if not engine.is_ready:
            await engine.refresh_data()
            
        if request.user_id:
            results = await engine.recommend_for_user(request.user_id)
        else:
            if not request.selected_genres:
                # Misafir için hiçbir tür seçilmemişse en popüler 10 filmi döndür
                # engine.recommend_for_guest([]) zaten bunu yapabilir ama garantiye alalım
                pass
            results = await engine.recommend_for_guest(request.selected_genres)
            
        if isinstance(results, dict) and "error" in results:
            raise HTTPException(status_code=404, detail=results["error"])
            
        return results
    except Exception as e:
        print(f"Öneri hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/refresh")
async def refresh_engine():
    """Motorun verilerini manuel olarak tazeler."""
    try:
        await engine.refresh_data()
        return {"message": "Motor başarıyla tazelendi", "movie_count": len(engine.movies_df)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
