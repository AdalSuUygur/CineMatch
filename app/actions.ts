"use server";

import { createPool } from "@vercel/postgres";
import { Movie } from "@/lib/api";

const pool = createPool({
  connectionString: process.env.POSTGRES_URL || process.env.DATABASE_URL
});

export async function fetchMoviesAction(offset: number = 0, limit: number = 20, genreIds?: number[]) {
  console.log(`[Server Action] fetchMoviesAction: offset=${offset}, limit=${limit}, genreIds=${genreIds}`);
  try {
    let query = `SELECT * FROM movies`;
    let params: any[] = [limit, offset];
    let paramIndex = 1;

    if (genreIds && genreIds.length > 0) {
      // Joining with movie_genres for filtering
      query = `
        SELECT m.* FROM movies m
        JOIN movie_genres mg ON m."movieId" = mg.movie_id
        WHERE mg.genre_id = ANY($1)
      `;
      params = [genreIds, limit, offset];
      paramIndex = 2;
    }

    query += ` ORDER BY "popularity" DESC NULLS LAST LIMIT $${paramIndex} OFFSET $${paramIndex + 1}`;

    const { rows } = await pool.query<Movie>(query, params);
    console.log(`[Server Action] Fetched ${rows.length} movies.`);
    return rows;
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
