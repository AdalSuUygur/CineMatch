"""
Chat API endpoint'leri - CineMatch AI Engine Entegrasyonu
"""
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from openai import AsyncOpenAI
from pathlib import Path
from dotenv import load_dotenv

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.src.db_pg import async_session_maker
from backend.src.models_pg import User, Interaction, Genre, Movie

# Root .env dosyasını bul ve yükle
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    user_id: Optional[int] = None

class CineMatchEngine:
    def __init__(self):
        # OpenAI API Key .env'den alınır
        api_key = os.getenv("OPENAI_API_KEY")
        # Asenkron client kullan
        self.client = AsyncOpenAI(api_key=api_key)

    async def get_personalized_recommendation(self, user_id: int, user_message: str):
        try:
            async with async_session_maker() as session:
                # 1. Kullanıcıyı ve Tercihlerini Çek
                result_user = await session.execute(select(User).where(User.user_id == user_id))
                user = result_user.scalars().first()
                if not user:
                    return "Kullanıcı profiliniz veritabanında bulunamadı."
                    
                # Etkileşim geçmişi ve türler
                result_interact = await session.execute(select(Interaction).where(Interaction.user_id == user_id))
                interactions = result_interact.scalars().all()
                
                result_genres = await session.execute(select(Genre))
                genres_list = result_genres.scalars().all()
                genre_map = {g.genre_id: g.genre_name for g in genres_list}
                
                # Kullanıcının seçtiği tür isimlerini belirle
                fav_genre_names = [genre_map.get(gid) for gid in (user.selected_genres or []) if genre_map.get(gid)]
                
                # 2. Etkileşim Geçmişinden Özet Çıkar
                liked_movies_metadata = []
                disliked_ids = []
                
                for inter in interactions:
                    result_movie = await session.execute(select(Movie).where(Movie.movieId == inter.movie_id))
                    movie = result_movie.scalars().first()
                    if movie:
                        if inter.is_liked:
                            metadata_str = str(movie.llm_metadata) if movie.llm_metadata else str(movie.title)
                            liked_movies_metadata.append(metadata_str)
                        elif inter.is_liked is False:
                            disliked_ids.append(inter.movie_id)
                            
                # 3. Aday Havuzu Oluştur
                watched_ids = [i.movie_id for i in interactions]
                exclude_ids = list(set(watched_ids + disliked_ids))
                
                stmt_candidates = select(Movie).where(
                    Movie.movieId.notin_(exclude_ids) & (Movie.vote_average > 6.0)
                ).order_by(Movie.popularity.desc()).limit(15)
                
                result_candidates = await session.execute(stmt_candidates)
                candidates = result_candidates.scalars().all()
                candidate_context = "\n".join([str(c.llm_metadata) if c.llm_metadata else str(c.title) for c in candidates])
                
            # 4. LLM Promptu
            system_prompt = f"""
            Sen CineMatch film uzmanısın. Kullanıcının zevkini analiz ederek ona en iyi tavsiyeleri verirsin.
            
            KULLANICI VERİLERİ (Hiyerarşik Öncelik):
            1. KULLANICININ MEVCUT LİSTESİ ("Listem" - En Önemli): {liked_movies_metadata[:10]}
            2. Kayıtta seçtiği genel favori türler: {fav_genre_names}
            
            GÖREV VE ÖNCELİK KURALLARI:
            - BİRİNCİL ÖNCELİK "LİSTEM": Kullanıcının zevkini belirleyen ana unsur "Listem"deki filmlerdir. Türler sadece ek bilgidir.
            - LİSTEDEN SEÇİM TALEBİ: Eğer kullanıcı "Listemden film seç", "Listemden ne izleyeyim?" gibi kendi listesiyle ilgili bir şey sorarsa, ADAY LİSTESİ'ni DEĞİL, yukarıdaki "KULLANICININ MEVCUT LİSTESİ" içerisinden seçim yap ve nedenini açıkla.
            - YENİ ÖNERİ TALEBİ: Eğer kullanıcı genel bir öneri isterse, "ADAY LİSTESİ"nden seçim yap. Bu seçimi yaparken mutlaka "Listem"deki filmlerle benzerlik kur. (Örn: "Listendeki **Inception** gibi akıl oyunlarını sevdiğin için aday listesinden şu filmi seçtim...")
            
            KESİN KURALLAR:
            1. Yeni öneri verirken sadece aşağıda verilen "ADAY LİSTESİ" içerisindeki filmleri kullan. Dışarıdan film uydurma.
            2. Film isimlerini mutlaka **Kalın Yazı** formatında kullan.
            3. Cevaplarını paragraflar halinde yaz, her öneri arasında boşluk bırak.
            
            ADAY LİSTESİ:
            {candidate_context}
            
            Cevabını Türkçe, samimi ve uzman bir dille ver.
            """

            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Öneri motoru işlem sırasında bir hata aldı: {str(e)}"

# Engine instance
engine = CineMatchEngine()

@router.post("")
async def chat_with_ai(request: ChatRequest):
    """CineMatch AI Engine ile kişiselleştirilmiş yanıt döndür"""
    # Debug için payload kontrolü yapalım (Opsiyonel)
    if request.user_id is None:
        raise HTTPException(status_code=401, detail="Chatbotu kullanmak için giriş yapmalısınız.")
        
    try:
        response = await engine.get_personalized_recommendation(request.user_id, request.message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sunucu hatası: {str(e)}")
