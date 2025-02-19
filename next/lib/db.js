import { Client } from 'pg';

const client = new Client({
  connectionString: process.env.POSTGRES_URL,
});

async function connectClient() {
  if (!client._connected) {
    await client.connect();
    client._connected = true;
  }
}

export async function query(text, params) {
  await connectClient();
  return await client.query(text, params);
}

process.on('exit', async () => {
  await client.end();
});

// import { Pool } from "pg";

// const pool = new Pool({
//   connectionString: process.env.POSTGRES_URL,
//   ssl: {
//     rejectUnauthorized: false, // Use true in production
//     require: true
//   }
// });

// async function connectPool() {
//   if (!pool._connected) {
//     await pool.connect();
//     pool._connected = true;
//   }
// }

// export async function query(text, params) {
//   await connectPool();
//   return await pool.query(text, params);
// }

// process.on('exit', async () => {
//   await pool.end();
// });