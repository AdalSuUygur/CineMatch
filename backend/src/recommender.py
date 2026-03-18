# DB-driven recommender - no cosine similarity OOM
from sqlalchemy.future import select
from sqlalchemy import desc, and_, or_, func
import pandas as pd
import numpy as np

from backend.src.db_pg import engine as db_engine, async_session_maker
from backend.src.models_pg import Movie, User, Interaction, Genre, MovieGenre


class CineMatchEngine:
    def __init__(self):
        self.is_ready = False

    async def refresh_data(self):
        """Sadece hazır bayrağını ayarlar (ağır hesaplama yok)."""
        self.is_ready = True
        print(" Motor Hazır (DB-driven mod).")

    async def get_genre_names(self, genre_ids):
        """Sayısal Tür ID'lerini 'Action' gibi isimlere çevirir."""
        if not genre_ids:
            return []
        async with async_session_maker() as session:
            result = await session.execute(select(Genre).where(Genre.genre_id.in_(genre_ids)))
            genres = result.scalars().all()
            return [g.genre_name for g in genres]

    async def recommend_for_guest(self, selected_genre_ids, skip: int = 0, limit: int = 20):
        """GUEST: Seçili türlerde 1990+ yüksek puanlı ve rastgele filmler döner."""
        async with async_session_maker() as session:
            if selected_genre_ids:
                genre_movie_ids_result = await session.execute(
                    select(MovieGenre.movie_id)
                    .where(MovieGenre.genre_id.in_(selected_genre_ids))
                    .distinct()
                )
                genre_movie_ids = [r[0] for r in genre_movie_ids_result.fetchall()]

                if genre_movie_ids:
                    stmt = (
                        select(Movie)
                        .where(Movie.movieId.in_(genre_movie_ids))
                        .where(Movie.vote_average > 6.0)
                        .where(Movie.release_date >= '1990-01-01')
                        .order_by(func.random())
                        .offset(skip)
                        .limit(limit)
                    )
                else:
                    stmt = (select(Movie)
                            .where(Movie.vote_average > 5.0)
                            .where(Movie.release_date >= '1990-01-01')
                            .order_by(func.random()).offset(skip).limit(limit))
            else:
                stmt = (select(Movie)
                        .where(Movie.vote_average > 5.0)
                        .where(Movie.release_date >= '1990-01-01')
                        .order_by(func.random()).offset(skip).limit(limit))

            result = await session.execute(stmt)
            movies = result.scalars().all()

        return self._format_movies(movies)

    async def recommend_for_user(self, user_id, skip: int = 0, limit: int = 20):
        """LOGIN: Kullanıcının selected_genres + beğendiği filmlere göre öneri yapar."""
        async with async_session_maker() as session:
            result_user = await session.execute(select(User).where(User.user_id == user_id))
            user = result_user.scalars().first()
            if not user:
                return {"error": "Kullanıcı bulunamadı"}

            fav_genre_ids = user.selected_genres or []

            # Get liked movie IDs
            result_interact = await session.execute(
                select(Interaction).where(
                    and_(Interaction.user_id == user_id, Interaction.is_liked == True)
                )
            )
            liked_interactions = result_interact.scalars().all()
            liked_movie_ids = [i.movie_id for i in liked_interactions]
            all_watched_ids = [i.movie_id for i in (await session.execute(
                select(Interaction).where(Interaction.user_id == user_id)
            )).scalars().all()]

            # Build candidate pool: movies in user's fav genres, not yet watched
            candidate_ids = []
            if fav_genre_ids:
                genre_movie_res = await session.execute(
                    select(MovieGenre.movie_id)
                    .where(MovieGenre.genre_id.in_(fav_genre_ids))
                    .distinct()
                )
                candidate_ids = [r[0] for r in genre_movie_res.fetchall()]

            # Also include movies from genres of liked films
            if liked_movie_ids:
                liked_genre_ids_res = await session.execute(
                    select(MovieGenre.genre_id)
                    .where(MovieGenre.movie_id.in_(liked_movie_ids))
                    .distinct()
                )
                liked_genre_ids = [r[0] for r in liked_genre_ids_res.fetchall()]
                if liked_genre_ids:
                    extra_movies_res = await session.execute(
                        select(MovieGenre.movie_id)
                        .where(MovieGenre.genre_id.in_(liked_genre_ids))
                        .distinct()
                    )
                    candidate_ids = list(set(candidate_ids + [r[0] for r in extra_movies_res.fetchall()]))

            # Exclude watched movies
            candidate_ids = [mid for mid in candidate_ids if mid not in all_watched_ids]

            if not candidate_ids:
                stmt = (
                    select(Movie)
                    .where(Movie.movieId.notin_(all_watched_ids) if all_watched_ids else True)
                    .where(Movie.vote_average > 5.0)
                    .where(Movie.release_date >= '1990-01-01')
                    .order_by(func.random())
                    .offset(skip)
                    .limit(limit)
                )
            else:
                stmt = (
                    select(Movie)
                    .where(Movie.movieId.in_(candidate_ids))
                    .where(Movie.vote_average > 5.5)
                    .where(Movie.release_date >= '1990-01-01')
                    .order_by(func.random())
                    .offset(skip)
                    .limit(limit)
                )

            result = await session.execute(stmt)
            movies = result.scalars().all()

        return self._format_movies(movies)

    def _format_movies(self, movies):
        """SQLAlchemy model listesini frontend dict listesine çevirir."""
        results = []
        for m in movies:
            results.append({
                "movieId": m.movieId,
                "_id": str(m.movieId),
                "title": m.title,
                "original_language": m.original_language or "en",
                "vote_average": m.vote_average or 0.0,
                "release_date": str(m.release_date) if m.release_date else "",
                "poster_url": m.poster_url or "",
                "popularity": m.popularity or 0.0,
                "llm_metadata": m.llm_metadata or "",
                "avg_rating": m.avg_rating or 0.0,
                "rating_count": m.rating_count or 0,
            })
        return results


# Singleton instance
engine = CineMatchEngine()
