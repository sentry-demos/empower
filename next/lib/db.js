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