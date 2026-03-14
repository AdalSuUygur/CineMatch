from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, ARRAY, JSON
from sqlalchemy.orm import relationship
from backend.src.db_pg import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, unique=True, index=True)
    full_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)  # In real world, hash this!
    selected_genres = Column(ARRAY(Integer), default=[])
    
    interactions = relationship("Interaction", back_populates="user")


class Movie(Base):
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    movieId = Column(Integer, unique=True, index=True) # Eşdeğer ID (Dataset ID)
    title = Column(String, index=True)
    original_title = Column(String, nullable=True)
    original_language = Column(String, nullable=True)
    popularity = Column(Float, nullable=True)
    release_date = Column(String, nullable=True)
    runtime = Column(Integer, nullable=True)
    vote_average = Column(Float, nullable=True)
    rating_count = Column(Integer, nullable=True)
    poster_url = Column(String, nullable=True)
    overview = Column(String, nullable=True)
    
    # Optional / Extra fields for LLM mappings
    llm_metadata = Column(JSON, nullable=True)
    
    interactions = relationship("Interaction", back_populates="movie")


class Genre(Base):
    __tablename__ = "genres"
    
    genre_id = Column(Integer, primary_key=True, index=True)
    genre_name = Column(String, unique=True)


class MovieGenre(Base):
    __tablename__ = "movie_genres"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    movie_id = Column(Integer, ForeignKey("movies.movieId"), index=True)
    genre_id = Column(Integer, ForeignKey("genres.genre_id"), index=True)


class Interaction(Base):
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    interaction_id = Column(Integer, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    movie_id = Column(Integer, ForeignKey("movies.movieId"))
    is_liked = Column(Boolean, default=False)
    rating = Column(Float, default=0.0)
    
    user = relationship("User", back_populates="interactions")
    movie = relationship("Movie", back_populates="interactions")
