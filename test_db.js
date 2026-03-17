const { createPool } = require('@vercel/postgres');
const dotenv = require('dotenv');
const path = require('path');

dotenv.config({ path: path.join(__dirname, '.env') });

const pool = createPool({
  connectionString: process.env.DATABASE_URL
});

async function test() {
  console.log("Connecting to:", process.env.DATABASE_URL ? "URL present" : "URL MISSING");
  try {
    const moviesRes = await pool.query('SELECT * FROM movies LIMIT 1');
    if (moviesRes.rows[0]) {
        console.log("Movies columns:", Object.keys(moviesRes.rows[0]));
    } else {
        console.log("Movies table is empty!");
    }
    
    const genresRes = await pool.query('SELECT * FROM movie_genres LIMIT 1');
    if (genresRes.rows[0]) {
        console.log("Movie-Genres columns:", Object.keys(genresRes.rows[0]));
        const countRes = await pool.query('SELECT count(*) FROM movie_genres');
        console.log("Movie-Genres count:", countRes.rows[0].count);
    } else {
        console.log("Movie-Genres table is empty!");
    }
  } catch (err) {
    console.error("DB Error:", err);
  } finally {
    process.exit();
  }
}

test();
