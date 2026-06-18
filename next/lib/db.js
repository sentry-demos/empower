import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.POSTGRES_URL,
  ssl: {
    require: true
  }
});

export async function query(text, params) {
  return await pool.query(text, params);
}

process.on('exit', async () => {
  await pool.end();
});
