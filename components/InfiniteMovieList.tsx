"use client";

import { useEffect, useState } from "react";
import { useInView } from "react-intersection-observer";
import { fetchMoviesAction } from "@/app/actions";
import { Movie, getMovieId } from "@/lib/api";
import MovieCard from "@/components/MovieCard";

interface InfiniteMovieListProps {
  initialMovies: Movie[];
  onAdd: (m: Movie) => Promise<void>;
  onRemove: (m: Movie) => Promise<void>;
  isWatched: (m: Movie) => boolean;
}

const styles = {
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
    gap: '2rem',
    padding: '2rem 4%',
  },
  loadingContainer: {
    padding: '2rem',
    textAlign: 'center' as const,
    color: '#b8c5d6',
    fontSize: '1.2rem',
    fontWeight: 600,
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    gap: '1rem',
  },
  loadMoreBtn: {
    padding: '0.75rem 2rem',
    borderRadius: '2rem',
    border: '1px solid #e50914',
    background: 'rgba(229, 9, 20, 0.1)',
    color: '#e50914',
    cursor: 'pointer',
    fontWeight: 700,
    transition: '0.3s',
  }
};

export default function InfiniteMovieList({ 
  initialMovies, 
  onAdd, 
  onRemove, 
  isWatched 
}: InfiniteMovieListProps) {
  const [movies, setMovies] = useState<Movie[]>(initialMovies);
  const [offset, setOffset] = useState(initialMovies.length);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const { ref, inView } = useInView({
    threshold: 0,
    rootMargin: '200px', // Trigger earlier
  });

  useEffect(() => {
    console.log(`[InfiniteMovieList] inView: ${inView}, loading: ${loading}, hasMore: ${hasMore}`);
    if (inView && !loading && hasMore) {
      loadMoreMovies();
    }
  }, [inView, loading, hasMore]);

  // If initialMovies was empty, retry once
  useEffect(() => {
    if (movies.length === 0 && hasMore && !loading) {
        loadMoreMovies();
    }
  }, []);

  const loadMoreMovies = async () => {
    if (loading || !hasMore) return;
    setLoading(true);
    console.log(`[InfiniteMovieList] Loading more movies from offset ${offset}...`);
    try {
      const newMovies = await fetchMoviesAction(offset, 24);
      console.log(`[InfiniteMovieList] Received ${newMovies.length} new movies.`);
      if (newMovies.length === 0) {
        setHasMore(false);
      } else {
        setMovies((prev) => {
          const prevIds = new Set(prev.map(m => getMovieId(m)));
          const filtered = newMovies.filter(m => !prevIds.has(getMovieId(m)));
          return [...prev, ...filtered];
        });
        setOffset((prev) => prev + newMovies.length);
      }
    } catch (error) {
      console.error("[InfiniteMovieList] Failed to load more movies:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section>
      <div style={styles.grid}>
        {movies.map((movie: Movie) => (
          <MovieCard
            key={getMovieId(movie)}
            movie={movie}
            onAdd={onAdd}
            onRemove={onRemove}
            isWatched={isWatched(movie)}
          />
        ))}
      </div>
      
      {hasMore && (
        <div ref={ref} style={styles.loadingContainer}>
          {loading ? (
            "🍿 Yeni filmler getiriliyor..."
          ) : (
            <>
              <span>Daha fazlası için kaydırın</span>
              <button 
                onClick={loadMoreMovies} 
                style={styles.loadMoreBtn}
              >
                Daha Fazla Yükle
              </button>
            </>
          )}
        </div>
      )}
      
      {!hasMore && movies.length > 0 && (
        <div style={styles.loadingContainer}>
          ✨ Tüm filmleri keşfettiniz ({movies.length} film)!
        </div>
      )}

      {movies.length === 0 && !loading && !hasMore && (
        <div style={styles.loadingContainer}>
          📭 Hiç film bulunamadı.
        </div>
      )}
    </section>
  );
}
