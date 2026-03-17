# Heavy imports moved inside methods to prevent OOM on serverless startup
from sqlalchemy.future import select

from backend.src.db_pg import engine as db_engine, async_session_maker
from backend.src.models_pg import Movie, User, Interaction, Genre

class CineMatchEngine:
    def __init__(self):
        self._movies_df = None  # Lazy loading via property
        self.cosine_sim = None
        self.count_matrix = None
        self.is_ready = False

    @property
    def movies_df(self):
        import pandas as pd
        if self._movies_df is None:
            self._movies_df = pd.DataFrame()
        return self._movies_df

    @movies_df.setter
    def movies_df(self, value):
        self._movies_df = value

    async def refresh_data(self):
        """Database'deki tüm filmleri çekip matematiksel modele hazırlar."""
        import pandas as pd
        async with async_session_maker() as session:
            result = await session.execute(select(Movie))
            movies_list = [{"movieId": m.movieId, "id": m.id, "title": m.title, "original_language": m.original_language,
                            "vote_average": m.vote_average, "release_date": m.release_date, "popularity": m.popularity,
                            "poster_url": m.poster_url, "llm_metadata": m.llm_metadata} for m in result.scalars().all()]
            
        self.movies_df = pd.DataFrame(movies_list)
        
        if self.movies_df.empty:
            print(" HATA: Veritabanı boş dönüyor!")
            self.is_ready = False
            return

        import pandas as pd
        # Tarih formatı
        if 'release_date' in self.movies_df.columns:
            self.movies_df['release_date'] = pd.to_datetime(self.movies_df['release_date'], errors='coerce')
            self.movies_df['year'] = self.movies_df['release_date'].dt.year.fillna(0).astype(int)
        
        # Beyni (Matematiksel Motoru) Hazırla
        self.prepare_engine()
        self.is_ready = True
        print(f" Motor Hazır: {len(self.movies_df)} film başarıyla yüklendi.")

        import pandas as pd
        import numpy as np
        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        from sklearn.preprocessing import MinMaxScaler

        # Metin benzerliği ve popülerlik normalizasyonu.
        self.count = CountVectorizer(stop_words='english')
        
        # Eğer llm_metadata dict ise string'e çevir, string ise doğrudan kullan
        metadata_series = self.movies_df['llm_metadata'].apply(
            lambda x: str(x) if isinstance(x, dict) else (x if pd.notnull(x) else '')
        )
        self.count_matrix = self.count.fit_transform(metadata_series)
        self.cosine_sim = cosine_similarity(self.count_matrix)
        
        # Popülerlik verisini 0-1 arasına sıkıştır
        scaler = MinMaxScaler()
        if 'popularity' in self.movies_df.columns:
            self.movies_df['norm_popularity'] = scaler.fit_transform(self.movies_df[['popularity']].fillna(0))
        else:
            self.movies_df['norm_popularity'] = 0

    async def get_genre_names(self, genre_ids):
        """Sayısal Tür ID'lerini 'Action' gibi isimlere çevirir."""
        if not genre_ids:
            return []
            
        async with async_session_maker() as session:
            result = await session.execute(select(Genre).where(Genre.genre_id.in_(genre_ids)))
            genres = result.scalars().all()
            return [g.genre_name for g in genres]

    async def recommend_for_guest(self, selected_genre_ids):
        """GUEST: Sadece seçtiği 1-3 tür üzerinden popüler olanları getirir."""
        if not self.is_ready:
            await self.refresh_data()
            
        genre_names = await self.get_genre_names(selected_genre_ids)
        if not genre_names:
            top_indices = self.movies_df.sort_values(by='norm_popularity', ascending=False).index[:10]
            return self.format_output(top_indices)
            
        query = "|".join(genre_names)
        
        import pandas as pd
        metadata_series = self.movies_df['llm_metadata'].apply(
            lambda x: str(x) if isinstance(x, dict) else (x if pd.notnull(x) else '')
        )
        mask = metadata_series.str.contains(query, case=False, na=False)
        subset = self.movies_df[mask].copy()
        
        if subset.empty:
            top_indices = self.movies_df.sort_values(by='norm_popularity', ascending=False).index[:10]
            return self.format_output(top_indices)
        
        subset['guest_score'] = subset['vote_average'].fillna(0) * 0.1 + subset['norm_popularity'] * 0.2
        
        top_indices = subset.sort_values(by='guest_score', ascending=False).index[:10]
        return self.format_output(top_indices)

    async def recommend_for_user(self, user_id):
        """LOGIN: Kullanıcının selected_genres + beğendiği filmlere bakar."""
        if not self.is_ready:
            await self.refresh_data()

        async with async_session_maker() as session:
            result_user = await session.execute(select(User).where(User.user_id == user_id))
            user = result_user.scalars().first()
            if not user: return {"error": "Kullanıcı bulunamadı"}

            fav_genres_ids = user.selected_genres or []
            
            result_interact = await session.execute(
                select(Interaction).where((Interaction.user_id == user_id) & (Interaction.is_liked == True))
            )
            interactions = result_interact.scalars().all()

        if not fav_genres_ids and not interactions:
            top_indices = self.movies_df.sort_values(by='norm_popularity', ascending=False).index[:10]
            return self.format_output(top_indices)

        fav_genres = await self.get_genre_names(fav_genres_ids)
        
        import numpy as np
        import pandas as pd
        
        final_scores = np.zeros(len(self.movies_df))
        
        for interact in interactions:
            m_id = interact.movie_id
            rating_weight = (interact.rating or 3.0) / 5.0
            try:
                idx_list = self.movies_df[self.movies_df['movieId'] == m_id].index
                if idx_list.empty:
                    idx_list = self.movies_df[self.movies_df['id'] == m_id].index
                
                if not idx_list.empty:
                    idx = idx_list[0]
                    final_scores += self.cosine_sim[idx] * rating_weight
            except Exception as e:
                print(f"Benzerlik hesaplama hatası (movie_id: {m_id}): {e}")
                continue

        genre_mask = np.zeros(len(self.movies_df))
        if fav_genres:
            genre_query = "|".join(fav_genres)
            metadata_str = self.movies_df['llm_metadata'].apply(
                lambda x: str(x) if isinstance(x, dict) else (x if pd.notnull(x) else '')
            )
            genre_mask = metadata_str.str.contains(genre_query, case=False, na=False).astype(int).values
        
        total_scores = (final_scores * 0.5) + (genre_mask * 0.3) + (self.movies_df['norm_popularity'] * 0.2)
        
        top_indices = np.argsort(total_scores)[::-1][:10]
        return self.format_output(top_indices)

    def format_output(self, indices):
        """Frontend'e temiz veri döner."""
        import pandas as pd
        results = []
        for idx in indices:
            row = self.movies_df.iloc[idx]
            results.append({
                "movieId": int(row['movieId']) if 'movieId' in row and pd.notnull(row['movieId']) else int(row['id']) if 'id' in row and pd.notnull(row['id']) else 0,
                "title": row['title'],
                "original_language": row.get('original_language', 'en'),
                "vote_average": float(row['vote_average']) if pd.notnull(row['vote_average']) else 0.0,
                "release_date": str(row['release_date']) if pd.notnull(row['release_date']) else "",
                "poster_url": row.get('poster_url', ''),
                "llm_metadata": row.get('llm_metadata', '')
            })
        return results

# Singleton instance
engine = CineMatchEngine()
