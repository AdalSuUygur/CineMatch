"use client";

import { useEffect, useState } from "react";
import InfiniteMovieList from "@/components/InfiniteMovieList";
import { fetchMoviesAction } from "@/app/actions";
import { Movie, getMovieId, addInteraction, deleteInteraction } from "@/lib/api";
import ChatBot from "@/components/ChatBot";

const styles = {
  main: {
    minHeight: '100vh',
    backgroundColor: '#0a0e1a',
    color: '#ffffff',
    fontFamily: "'Inter', sans-serif",
  },
  container: {
    padding: '2rem 0',
  },
  titleSection: {
    padding: '4rem 4% 2rem 4%',
  },
  title: {
    fontSize: '3rem',
    fontWeight: 900,
    background: 'linear-gradient(135deg, #e50914, #ff6b6b)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    marginBottom: '0.5rem',
  },
  subtitle: {
    fontSize: '1.2rem',
    color: '#b8c5d6',
    maxWidth: '600px',
  },
};

export default function MoviesPage() {
  const [initialMovies, setInitialMovies] = useState<Movie[]>([]);
  const [user, setUser] = useState<any>(null);
  const [watchedMovies, setWatchedMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedGenreIds, setSelectedGenreIds] = useState<number[]>([]);

  useEffect(() => {
    const savedUser = localStorage.getItem('currentUser');
    let genreIds: number[] = [];
    if (savedUser) {
      const parsedUser = JSON.parse(savedUser);
      setUser(parsedUser);
      genreIds = parsedUser.selected_genres || [];
      setSelectedGenreIds(genreIds);
      const savedWatched = localStorage.getItem(`watched_${parsedUser.user_id}`);
      if (savedWatched) setWatchedMovies(JSON.parse(savedWatched));
    }

    loadInitialData(genreIds);
  }, []);

  // Initial data fetch
  const loadInitialData = async (genreIds: number[]) => {
    try {
      console.log("[MoviesPage] Loading initial movies with genres:", genreIds);
      const movies = await fetchMoviesAction(0, 24, genreIds);
      setInitialMovies(movies);
    } catch (err) {
      console.error("Failed to load initial movies", err);
    } finally {
      setLoading(false);
    }
  };

  const addToWatched = async (m: Movie) => {
    if (!user) {
      window.dispatchEvent(new CustomEvent('open-auth'));
      return;
    }
    const mid = getMovieId(m);
    if (!watchedMovies.some(x => getMovieId(x) === mid)) {
      const newList = [m, ...watchedMovies];
      setWatchedMovies(newList);
      localStorage.setItem(`watched_${user.user_id}`, JSON.stringify(newList));
      await addInteraction(user.user_id, mid, true, 5);
    }
  };

  const removeFromWatched = async (m: Movie) => {
    if (!user) return;
    const mid = getMovieId(m);
    const newList = watchedMovies.filter(x => getMovieId(x) !== mid);
    setWatchedMovies(newList);
    localStorage.setItem(`watched_${user.user_id}`, JSON.stringify(newList));
    await deleteInteraction(user.user_id, mid);
  };

  const isWatched = (m: Movie) => watchedMovies.some(x => getMovieId(x) === getMovieId(m));

  return (
    <main style={styles.main}>
      <div style={styles.container}>
        <section style={styles.titleSection}>
          <h1 style={styles.title}>Tüm Filmleri Keşfet</h1>
          <p style={styles.subtitle}>
            Popülerlik sırasına göre binlerce yapım arasından sana en uygun olanı bul.
          </p>
        </section>

        {loading ? (
          <div style={{ padding: '4rem', textAlign: 'center', color: '#b8c5d6' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🎬</div>
            <p>Filmler hazırlanıyor...</p>
          </div>
        ) : (
          <InfiniteMovieList
            initialMovies={initialMovies}
            onAdd={addToWatched}
            onRemove={removeFromWatched}
            isWatched={isWatched}
            genreIds={selectedGenreIds}
          />
        )}
      </div>

      <ChatBot />
    </main>
  );
}
