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
    const { rows } = await pool.query('SELECT title FROM movies LIMIT 5');
    console.log("Success! Sample movies:");
    rows.forEach(r => console.log("- " + r.title));
  } catch (err) {
    console.error("DB Error:", err);
  } finally {
    process.exit();
  }
}

test();
