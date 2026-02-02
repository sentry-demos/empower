import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.POSTGRES_URL,
  ssl: {
    require: true
  },
  max: 20, // Maximum number of clients in the pool
  idleTimeoutMillis: 30000, // Close idle clients after 30 seconds
  connectionTimeoutMillis: 10000, // Return an error after 10 seconds if connection could not be established
});

export async function query(text, params) {
  // Pool automatically handles connection checkout and return
  return await pool.query(text, params);
}

process.on('exit', async () => {
  await pool.end();
});