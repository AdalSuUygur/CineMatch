"use server";

import { createPool } from "@vercel/postgres";
import { Movie } from "@/lib/api";

const pool = createPool({
  connectionString: process.env.POSTGRES_URL || process.env.DATABASE_URL
});

export async function fetchMoviesAction(offset: number = 0, limit: number = 24, genreIds?: number[]) {
  const hasGenres = genreIds && genreIds.length > 0;
  console.log(`[Server Action] fetchMoviesAction: offset=${offset}, limit=${limit}, hasGenres=${hasGenres}`);
  
  try {
    let query = "";
    let params: any[] = [];

    if (hasGenres) {
      // Boost movies matching selected genres but show all if preferred? 
      // Actually, user said "türler algoritması", so let's do a JOIN for strict filtering
      // but if they want the WHOLE list with favorites first, we use LEFT JOIN.
      // Let's stick to strict filtering for now as it's more common for "genre selection".
      query = `
        SELECT DISTINCT m.* 
        FROM movies m
        INNER JOIN movie_genres mg ON m."movieId" = mg.movie_id
        WHERE mg.genre_id = ANY($1)
        ORDER BY m."popularity" DESC NULLS LAST, m."movieId" ASC
        LIMIT $2 OFFSET $3
      `;
      params = [genreIds, limit, offset];
    } else {
      query = `
        SELECT * FROM movies 
        ORDER BY "popularity" DESC NULLS LAST, "movieId" ASC 
        LIMIT $1 OFFSET $2
      `;
      params = [limit, offset];
    }

    const { rows } = await pool.query<any>(query, params);
    
    // Normalize rows (DB might return lowercase or snake_case)
    const normalizedRows = rows.map((r: any) => ({
      ...r,
      movieId: r.movieId || r.movieid || r.id,
      poster_url: r.poster_url || r.posterurl || r.image_url,
      release_date: r.release_date || r.releasedate,
      vote_average: Number(r.vote_average || r.voteaverage || r.rating || 0),
      llm_metadata: r.llm_metadata || r.llmmetadata || r.overview,
      title: r.title || r.isim,
    })) as Movie[];

    console.log(`[Server Action] Fetched ${normalizedRows.length} movies.`);
    return normalizedRows;
  } catch (error) {
    console.error("[Server Action] Failed to fetch movies:", error);
    return [];
  }
}

export async function fetchGenresAction() {
  try {
    const { rows } = await pool.query("SELECT * FROM genres ORDER BY genre_name ASC");
    return rows;
  } catch (error) {
    console.error("[Server Action] Failed to fetch genres:", error);
    return [];
  }
}
