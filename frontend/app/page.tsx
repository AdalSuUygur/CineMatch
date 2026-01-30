'use client';

import { useEffect, useState, useRef } from 'react';
import {
  getMovies,
  getGenres,
  Movie,
  Genre,
  getMovieId,
  saveUserPreferences,
  registerUser,
  loginUser,
  addInteraction,
  deleteInteraction,
  getUserInteractions,
  getRecommendations,
  User
} from '@/lib/api';
import MovieCard from '@/components/MovieCard';
import ChatBot from '@/components/ChatBot';

const styles = {
  main: {
    minHeight: '100vh',
    backgroundColor: '#0a0e1a',
    color: '#ffffff',
    fontFamily: "'Inter', sans-serif",
  },
  selectionScreen: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    padding: '2rem',
    background: 'radial-gradient(circle at center, #1a2235 0%, #0a0e1a 100%)',
  },
  authCard: {
    background: 'rgba(26, 34, 53, 0.8)',
    backdropFilter: 'blur(20px)',
    padding: '3rem',
    borderRadius: '1.5rem',
    width: '100%',
    maxWidth: '450px',
    boxShadow: '0 20px 50px rgba(0,0,0,0.5)',
    border: '1px solid rgba(255,255,255,0.1)',
  },
  input: {
    width: '100%',
    padding: '1rem',
    marginBottom: '1rem',
    borderRadius: '0.75rem',
    border: '1px solid #2a3548',
    backgroundColor: '#0a0e1a',
    color: 'white',
    fontSize: '1rem',
  },
  title: {
    fontSize: '3rem',
    fontWeight: 900,
    marginBottom: '1rem',
    textAlign: 'center' as const,
    background: 'linear-gradient(135deg, #e50914, #ff6b6b)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  subtitle: {
    fontSize: '1.1rem',
    color: '#b8c5d6',
    marginBottom: '2rem',
    textAlign: 'center' as const,
  },
  startBtn: {
    width: '100%',
    padding: '1rem',
    borderRadius: '0.75rem',
    border: 'none',
    background: 'linear-gradient(135deg, #e50914, #ff6b6b)',
    color: 'white',
    fontSize: '1.1rem',
    fontWeight: 700,
    cursor: 'pointer',
    marginTop: '1rem',
    transition: '0.3s',
  },
  hero: {
    height: '85vh',
    width: '100%',
    position: 'relative' as const,
    marginBottom: '2rem',
    display: 'flex',
    alignItems: 'center',
    padding: '0 4%',
    backgroundSize: 'cover',
    backgroundPosition: 'center top',
    transition: 'background-image 0.8s ease-in-out',
  },
  heroOverlay: {
    position: 'absolute' as const,
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'linear-gradient(to right, #0a0e1a 10%, rgba(10, 14, 26, 0.4) 50%, transparent 100%), linear-gradient(to top, #0a0e1a 0%, transparent 40%)',
    zIndex: 1,
  },
  heroContent: {
    maxWidth: '800px',
    position: 'relative' as const,
    zIndex: 2,
  },
  heroTitle: {
    fontSize: '4.5rem',
    fontWeight: 900,
    marginBottom: '1rem',
    lineHeight: 1.1,
    textShadow: '0 4px 20px rgba(0,0,0,0.5)',
  },
  heroDesc: {
    fontSize: '1.25rem',
    color: '#b8c5d6',
    marginBottom: '2rem',
    lineHeight: 1.6,
    textShadow: '0 2px 10px rgba(0,0,0,0.5)',
  },
  row: {
    marginBottom: '5rem',
  },
  rowTitle: {
    fontSize: '1.8rem',
    fontWeight: 800,
    marginBottom: '1.5rem',
    paddingLeft: '4%',
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
  },
  rowSlider: {
    display: 'flex',
    overflowX: 'auto' as const,
    gap: '1.5rem',
    padding: '1rem 4% 3rem 4%',
    scrollbarWidth: 'none' as const,
    scrollBehavior: 'smooth' as const,
  },
  sliderItem: {
    flexShrink: 0,
    transition: 'transform 0.3s',
  },
  arrowBtn: {
    position: 'absolute' as const,
    top: '50%',
    transform: 'translateY(-50%)',
    width: '50px',
    height: '50px',
    borderRadius: '50%',
    backgroundColor: 'rgba(10, 14, 26, 0.7)',
    backdropFilter: 'blur(10px)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    color: 'white',
    fontSize: '1.5rem',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    zIndex: 20,
    transition: '0.3s all',
    boxShadow: '0 4px 15px rgba(0,0,0,0.5)',
  }
};

export default function Home() {
  const [step, setStep] = useState<'selection' | 'home'>('selection');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isLogin, setIsLogin] = useState(true);
  const [user, setUser] = useState<User | null>(null);

  // Form fields
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');

  // Genre selection
  const [genres, setGenres] = useState<Genre[]>([]);
  const [selectedGenreIds, setSelectedGenreIds] = useState<number[]>([]);

  // Home data
  const [popularMovies, setPopularMovies] = useState<Movie[]>([]);
  const [recommendations, setRecommendations] = useState<Movie[]>([]);
  const [selectedGenreRows, setSelectedGenreRows] = useState<{ name: string, movies: Movie[] }[]>([]);
  const [otherGenreRows, setOtherGenreRows] = useState<{ name: string, movies: Movie[] }[]>([]);
  const [watchedMovies, setWatchedMovies] = useState<Movie[]>([]);

  // Hero Carousel
  const [heroIndex, setHeroIndex] = useState(0);
  const heroInterval = useRef<NodeJS.Timeout | null>(null);

  const [loading, setLoading] = useState(false);
  const [showGenreLimitModal, setShowGenreLimitModal] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);

  useEffect(() => {
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }

    const savedGenres = localStorage.getItem('genres_selected');
    if (savedGenres) {
      setSelectedGenreIds(JSON.parse(savedGenres));
    }

    // Check if returning from movie detail
    const isReturning = sessionStorage.getItem('returnFromDetail');
    if (isReturning === 'true') {
      setStep('home');
      sessionStorage.removeItem('returnFromDetail');
    }

    loadGenres();
  }, []);

  useEffect(() => {
    if (step === 'home') {
      loadHomeData();
      if (user) syncWatchedList();

      // Start hero carousel
      startCarousel();
    }
    return () => stopCarousel();
  }, [step, user]);

  const startCarousel = () => {
    stopCarousel();
    heroInterval.current = setInterval(() => {
      setHeroIndex(prev => (prev + 1) % 5);
    }, 6000);
  };

  const stopCarousel = () => {
    if (heroInterval.current) clearInterval(heroInterval.current);
  };

  useEffect(() => {
    const handleAuthTrigger = () => setShowAuthModal(true);
    const handleResetTrigger = () => {
      setStep('selection');
      setShowAuthModal(false);
    };

    window.addEventListener('open-auth', handleAuthTrigger);
    window.addEventListener('reset-selection', handleResetTrigger);

    return () => {
      window.removeEventListener('open-auth', handleAuthTrigger);
      window.removeEventListener('reset-selection', handleResetTrigger);
    };
  }, []);

  const loadGenres = async () => {
    try {
      const data = await getGenres();
      setGenres(data);
    } catch (e) { console.error(e); }
  };

  const handleAuth = async () => {
    setLoading(true);
    try {
      if (isLogin) {
        const res = await loginUser(email, password);
        setUser(res.user);
        localStorage.setItem('currentUser', JSON.stringify(res.user));
        if (res.user.selected_genres && res.user.selected_genres.length > 0) {
          setSelectedGenreIds(res.user.selected_genres);
          localStorage.setItem('genres_selected', JSON.stringify(res.user.selected_genres));
        }
        setShowAuthModal(false);
        setStep('home');
      } else {
        const res = await registerUser(fullName, email, password, selectedGenreIds);
        setUser(res.user);
        localStorage.setItem('currentUser', JSON.stringify(res.user));
        setShowAuthModal(false);
        setStep('home');
      }
    } catch (e: any) {
      setAuthError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleOnboarding = async () => {
    if (selectedGenreIds.length >= 1 && selectedGenreIds.length <= 3) {
      localStorage.setItem('genres_selected', JSON.stringify(selectedGenreIds));
      if (user) {
        try { await saveUserPreferences(user.user_id, selectedGenreIds); }
        catch (e) { console.error("Genre update failed", e); }
      }
      setStep('home');
    }
  };

  const loadHomeData = async () => {
    setLoading(true);
    try {
      const popular = await getMovies(0, 15, undefined, undefined, 'popularity');
      setPopularMovies(popular);

      if (selectedGenreIds.length > 0 || user) {
        const recs = await getRecommendations(user?.user_id || undefined, selectedGenreIds);
        setRecommendations(recs);

        // All genres to process
        const allGenreIds = genres.map(g => g.genre_id);

        const allRows = await Promise.all(
          allGenreIds.map(async (gid) => {
            const gName = genres.find(g => (g.genre_id === gid))?.genre_name || 'Tür';
            const movies = await getMovies(0, 10, undefined, [gid]);
            return { id: gid, name: gName, movies };
          })
        );

        const filteredRows = allRows.filter(r => r.movies.length > 0);

        // Bifurcate rows
        const selectedRows = filteredRows.filter(r => selectedGenreIds.includes(r.id));
        const nonSelectedRows = filteredRows.filter(r => !selectedGenreIds.includes(r.id));

        setSelectedGenreRows(selectedRows);
        setOtherGenreRows(nonSelectedRows);
      }
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const syncWatchedList = async () => {
    if (!user) return;
    try {
      const saved = localStorage.getItem(`watched_${user.user_id}`);
      if (saved) setWatchedMovies(JSON.parse(saved));
    } catch (e) { console.error(e); }
  };

  const addToWatched = async (m: Movie) => {
    if (!user) {
      setShowAuthModal(true);
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

  if (step === 'selection') {
    return (
      <div style={styles.selectionScreen}>
        <h1 style={styles.title}>Türlerini Seç</h1>
        <p style={styles.subtitle}>Sana özel öneriler için en sevdiğin 3 türü belirle.</p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(150px, 1fr))', gap: '1.25rem', maxWidth: '900px', width: '100%' }}>
          {genres.map(g => (
            <div
              key={g.genre_id}
              onClick={() => {
                if (selectedGenreIds.includes(g.genre_id)) setSelectedGenreIds(selectedGenreIds.filter(id => id !== g.genre_id));
                else if (selectedGenreIds.length < 3) setSelectedGenreIds([...selectedGenreIds, g.genre_id]);
                else setShowGenreLimitModal(true);
              }}
              style={{
                padding: '1.75rem 1.25rem',
                borderRadius: '1.25rem',
                border: selectedGenreIds.includes(g.genre_id) ? '3px solid #e50914' : '1px solid #2a3548',
                backgroundColor: selectedGenreIds.includes(g.genre_id) ? 'rgba(229, 9, 20, 0.15)' : 'rgba(26, 34, 53, 0.5)',
                textAlign: 'center',
                cursor: 'pointer',
                transition: '0.3s all cubic-bezier(0.4, 0, 0.2, 1)',
                transform: selectedGenreIds.includes(g.genre_id) ? 'scale(1.05)' : 'scale(1)',
                fontWeight: 600,
                fontSize: '1.1rem',
              }}
            >
              {g.genre_name}
            </div>
          ))}
        </div>
        <button
          style={{ ...styles.startBtn, maxWidth: '350px', opacity: (selectedGenreIds.length >= 1 && selectedGenreIds.length <= 3) ? 1 : 0.5, marginTop: '3rem' }}
          disabled={selectedGenreIds.length < 1 || selectedGenreIds.length > 3}
          onClick={handleOnboarding}
        >
          {selectedGenreIds.length > 0
            ? `Seçimleri Kaydet ve Başla (${selectedGenreIds.length}/3)`
            : 'En az 1 tür seçmelisiniz'}
        </button>

        {showGenreLimitModal && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.85)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 2000,
            backdropFilter: 'blur(10px)',
            animation: 'fadeIn 0.3s ease-out'
          }}>
            <div style={{
              background: 'rgba(26, 34, 53, 0.95)',
              padding: '3rem',
              borderRadius: '2rem',
              maxWidth: '400px',
              width: '90%',
              textAlign: 'center',
              border: '2px solid #e50914',
              boxShadow: '0 0 30px rgba(229, 9, 20, 0.3)',
              transform: 'scale(1)',
              animation: 'popIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)'
            }}>
              <div style={{ fontSize: '4rem', marginBottom: '1.5rem' }}>🛑</div>
              <h2 style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '1rem', color: '#ffffff' }}>Limit Doldu!</h2>
              <p style={{ color: '#b8c5d6', marginBottom: '2.5rem', lineHeight: 1.6, fontSize: '1.1rem' }}>
                En fazla 3 tür seçebilirsiniz. Devam etmek için önce seçimlerinden birini kaldırman gerekiyor.
              </p>
              <button
                onClick={() => setShowGenreLimitModal(false)}
                style={{
                  ...styles.startBtn,
                  marginTop: 0,
                  padding: '1rem 2rem'
                }}
              >
                Anladım
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }


  const currentHero = popularMovies[heroIndex] || popularMovies[0];
  const heroImg = currentHero?.poster_url || "https://images.unsplash.com/photo-1626814026160-2237a95fc5a0?q=80&w=2070&auto=format&fit=crop";

  return (
    <main style={styles.main}>
      <style>{`.no-scrollbar::-webkit-scrollbar { display: none; }`}</style>

      <section style={{ ...styles.hero, backgroundImage: `url(${heroImg})` }}>
        <div style={styles.heroOverlay} />
        <div style={styles.heroContent}>
          <h1 style={styles.heroTitle}>{currentHero?.title}</h1>
          <p style={styles.heroDesc}>{currentHero?.llm_metadata?.split(',').slice(0, 2).join(', ')}</p>
          <div style={{ display: 'flex', gap: '1.5rem' }}>
            <button
              onClick={() => currentHero && addToWatched(currentHero)}
              style={{ ...styles.startBtn, width: 'auto', padding: '1.25rem 2.5rem', marginTop: 0 }}
            >
              + Listeme Ekle
            </button>
            <button
              onClick={() => { setStep('selection'); }}
              style={{ ...styles.startBtn, width: 'auto', padding: '1.25rem 2.5rem', marginTop: 0, background: 'rgba(255,255,255,0.15)', backdropFilter: 'blur(10px)' }}
            >
              Türleri Güncelle
            </button>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '3rem' }}>
            {[0, 1, 2, 3, 4].map(i => (
              <div
                key={i}
                onClick={() => { setHeroIndex(i); startCarousel(); }}
                style={{
                  width: i === heroIndex ? '40px' : '10px',
                  height: '10px',
                  borderRadius: '10px',
                  background: i === heroIndex ? '#e50914' : 'rgba(255,255,255,0.3)',
                  transition: '0.4s',
                  cursor: 'pointer'
                }}
              />
            ))}
          </div>
        </div>
      </section>

      <div style={{ marginTop: '-15vh', position: 'relative', zIndex: 10 }}>
        <MovieRow title="Sizin İçin Önerilenler" movies={recommendations} onAdd={addToWatched} onRemove={removeFromWatched} isWatched={isWatched} />
        <MovieRow title="Listem" movies={watchedMovies} onAdd={addToWatched} onRemove={removeFromWatched} isWatched={isWatched} />
        <MovieRow title="Popüler Filmler" movies={popularMovies} onAdd={addToWatched} onRemove={removeFromWatched} isWatched={isWatched} />

        {/* Selected Genres */}
        {selectedGenreRows.map(row => (
          <MovieRow key={row.name} title={row.name} movies={row.movies} onAdd={addToWatched} onRemove={removeFromWatched} isWatched={isWatched} />
        ))}

        {/* Other Genres for exploration */}
        {otherGenreRows.map(row => (
          <MovieRow key={row.name} title={row.name} movies={row.movies} onAdd={addToWatched} onRemove={removeFromWatched} isWatched={isWatched} />
        ))}
      </div>
      {showAuthModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.8)',
          backdropFilter: 'blur(10px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
        }}>
          <div style={{ ...styles.authCard, position: 'relative' }}>
            <button
              onClick={() => setShowAuthModal(false)}
              style={{
                position: 'absolute',
                top: '1rem',
                right: '1rem',
                background: 'none',
                border: 'none',
                color: 'white',
                fontSize: '1.5rem',
                cursor: 'pointer',
              }}
            >
              ✕
            </button>
            <h1 style={styles.title}>CineMatch</h1>
            <p style={styles.subtitle}>{isLogin ? 'Listenizi kaydetmek için giriş yapın.' : 'Yeni listeniz için kayıt olun.'}</p>

            {!isLogin && (
              <input
                style={styles.input}
                placeholder="Tam Adınız"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            )}
            <input
              style={styles.input}
              placeholder="Email Adresiniz"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <input
              style={styles.input}
              type="password"
              placeholder="Şifreniz"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />

            <button style={styles.startBtn} onClick={handleAuth} disabled={loading}>
              {loading ? 'İşleniyor...' : (isLogin ? 'Giriş Yap' : 'Kayıt Ol')}
            </button>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginTop: '1.5rem' }}>
              <p style={{ textAlign: 'center', cursor: 'pointer', color: '#7a8ba3' }} onClick={() => setIsLogin(!isLogin)}>
                {isLogin ? 'Hesabınız yok mu? Kayıt olun.' : 'Zaten hesabınız var mı? Giriş yapın.'}
              </p>
              <button style={{ background: 'none', border: 'none', color: '#ff6b6b', cursor: 'pointer', fontWeight: 600 }} onClick={() => setShowAuthModal(false)}>
                Vazgeç, Misafir Olarak Devam Et ➔
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Auth Error Modal */}
      {authError && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.85)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 2000,
          backdropFilter: 'blur(10px)',
        }}>
          <div style={{
            background: 'rgba(26, 34, 53, 0.95)',
            padding: '3rem',
            borderRadius: '2rem',
            maxWidth: '450px',
            width: '90%',
            textAlign: 'center',
            border: '2px solid #e50914',
            boxShadow: '0 0 30px rgba(229, 9, 20, 0.3)',
          }}>
            <div style={{ fontSize: '4rem', marginBottom: '1.5rem' }}>⚠️</div>
            <h2 style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '1rem', color: '#ffffff' }}>Bir Hata Oluştu</h2>
            <p style={{ color: '#b8c5d6', marginBottom: '2.5rem', lineHeight: 1.6, fontSize: '1.1rem' }}>
              {authError}
            </p>
            <button
              onClick={() => setAuthError(null)}
              style={{
                ...styles.startBtn,
                marginTop: 0,
                padding: '1rem 2rem'
              }}
            >
              Anladım
            </button>
          </div>
        </div>
      )}
      <ChatBot />
    </main>
  );
}

const MovieRow = ({ title, movies, onAdd, onRemove, isWatched }: any) => {
  const sliderRef = useRef<HTMLDivElement>(null);
  const [showArrows, setShowArrows] = useState(false);

  if (movies.length === 0) return null;

  const scroll = (direction: 'left' | 'right') => {
    if (sliderRef.current) {
      const { scrollLeft, clientWidth } = sliderRef.current;
      const scrollTo = direction === 'left'
        ? scrollLeft - clientWidth * 0.8
        : scrollLeft + clientWidth * 0.8;

      sliderRef.current.scrollTo({ left: scrollTo, behavior: 'smooth' });
    }
  };

  return (
    <div
      style={{ ...styles.row, position: 'relative' }}
      onMouseEnter={() => setShowArrows(true)}
      onMouseLeave={() => setShowArrows(false)}
    >
      <h2 style={styles.rowTitle}>{title}</h2>

      {/* Left Arrow */}
      <button
        style={{
          ...styles.arrowBtn,
          left: '1%',
          opacity: showArrows ? 1 : 0,
          visibility: showArrows ? 'visible' : 'hidden',
          pointerEvents: showArrows ? 'auto' : 'none'
        }}
        onClick={() => scroll('left')}
        onMouseOver={(e) => (e.currentTarget.style.borderColor = '#e50914')}
        onMouseOut={(e) => (e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)')}
      >
        ‹
      </button>

      {/* Right Arrow */}
      <button
        style={{
          ...styles.arrowBtn,
          right: '1%',
          opacity: showArrows ? 1 : 0,
          visibility: showArrows ? 'visible' : 'hidden',
          pointerEvents: showArrows ? 'auto' : 'none'
        }}
        onClick={() => scroll('right')}
        onMouseOver={(e) => (e.currentTarget.style.borderColor = '#e50914')}
        onMouseOut={(e) => (e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)')}
      >
        ›
      </button>

      <div style={styles.rowSlider} className="no-scrollbar" ref={sliderRef}>
        {movies.map((movie: any) => (
          <div key={getMovieId(movie)} style={styles.sliderItem}>
            <MovieCard
              movie={movie}
              onAdd={onAdd}
              onRemove={onRemove}
              isWatched={isWatched(movie)}
            />
          </div>
        ))}
      </div>
    </div>
  );
};
