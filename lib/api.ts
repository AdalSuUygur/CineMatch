/**
 * API Service Layer
 * Backend ile iletişim için fonksiyonlar
 */

const getBaseUrl = () => {
    if (typeof window !== 'undefined') return ''; // Browser checks relative API path
    if (process.env.VERCEL_URL) return `https://${process.env.VERCEL_URL}`; // Vercel SSR Check
    return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'; // local / docker fallback
};

const API_BASE_URL = getBaseUrl();

// Generic fetch wrapper
async function fetchAPI<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        cache: 'no-store',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
}

// Movie type - flexible to handle vars MongoDB ioufield names
export interface Movie {
    _id?: string;
    movieId?: number;
    id?: number;
    title: string;
    imdbId?: number;
    tmdbId?: number;
    avg_rating?: number;
    rating_count?: number;
    original_language?: string;
    original_title?: string;
    popularity?: number;
    release_date?: any;
    runtime?: number;
    vote_average?: number;
    poster_url?: string;
    llm_metadata?: string;
    [key: string]: any; // Allow any additional fields
}

export interface User {
    _id?: string;
    user_id: number;
    full_name: string;
    email: string;
    selected_genres?: number[];
    [key: string]: any;
}

export interface UserInteraction {
    _id?: string;
    interaction_id: number;
    user_id: number;
    movie_id: number;
    is_liked: boolean;
    rating: number;
    selected_genres?: number[];
    [key: string]: any;
}

export interface Genre {
    _id?: string;
    genre_id: number;
    genre_name: string;
    [key: string]: any;
}

// Helper to get movie ID from various possible field names
export function getMovieId(movie: Movie): number {
    return movie.movieId || movie.id || 0;
}

// API Functions
export async function getMovies(
    skip: number = 0,
    limit: number = 20,
    search?: string,
    genreIds?: number[],
    sortBy?: string
): Promise<Movie[]> {
    let endpoint = `/api/movies?skip=${skip}&limit=${limit}`;
    if (search) {
        endpoint += `&search=${encodeURIComponent(search)}`;
    }
    if (genreIds && genreIds.length > 0) {
        endpoint += `&genre_ids=${genreIds.join(',')}`;
    }
    if (sortBy) {
        endpoint += `&sort_by=${sortBy}`;
    }
    return fetchAPI<Movie[]>(endpoint);
}

export async function getMovie(id: number): Promise<Movie> {
    return fetchAPI<Movie>(`/api/movies/${id}`);
}

export async function registerUser(fullName: string, email: string, password: string, selectedGenres: number[] = []): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/users/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ full_name: fullName, email, password, selected_genres: selectedGenres }),
    });
    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Registration failed');
    }
    return response.json();
}

export async function loginUser(email: string, password: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/users/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
    });
    if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || 'Login failed');
    }
    return response.json();
}

export async function saveUserPreferences(userId: number, selectedGenres: number[]): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/users/${userId}/preferences`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ selected_genres: selectedGenres }),
    });
    return response.json();
}

export async function addInteraction(userId: number, movieId: number, isLiked: boolean = true, rating: number = 5): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/interactions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, movie_id: movieId, is_liked: isLiked, rating }),
    });
    return response.json();
}

export async function deleteInteraction(userId: number, movieId: number): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/api/interactions/user/${userId}/movie/${movieId}`, {
        method: 'DELETE',
    });
    return response.json();
}

export async function getUserInteractions(
    userId: number,
    skip: number = 0,
    limit: number = 100
): Promise<UserInteraction[]> {
    return fetchAPI<UserInteraction[]>(`/api/interactions/user/${userId}?skip=${skip}&limit=${limit}`);
}

export async function searchMovies(query: string): Promise<Movie[]> {
    return fetchAPI<Movie[]>(`/api/movies/search/query?q=${encodeURIComponent(query)}`);
}

export async function getRecommendations(userId?: number, selectedGenres: number[] = []): Promise<Movie[]> {
    const response = await fetch(`${API_BASE_URL}/api/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, selected_genres: selectedGenres }),
    });
    if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        console.error('Recommendation API error:', err);
        return []; // Fallback to empty list or handle as needed
    }
    return response.json();
}

export async function getUsers(
    skip: number = 0,
    limit: number = 100
): Promise<User[]> {
    return fetchAPI<User[]>(`/api/users?skip=${skip}&limit=${limit}`);
}

export async function getUser(id: number): Promise<User> {
    return fetchAPI<User>(`/api/users/${id}`);
}

export async function getGenres(): Promise<Genre[]> {
    return fetchAPI<Genre[]>('/api/genres');
}

export async function sendChatMessage(message: string, userId?: number): Promise<string> {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, user_id: userId }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Chat API hatası: ${response.status}`);
    }

    const data = await response.json();
    return data.response;
}

export async function getMovieGenres(movieId: number): Promise<Genre[]> {
    return fetchAPI<Genre[]>(`/api/genres/movie/${movieId}`);
}
