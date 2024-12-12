## Local Development

### Database Setup

1. Start the PostgreSQL database using Docker Compose:

```bash
docker compose up -d
```

2. Create a `.env` file in the root directory using `.env.example` as a template:

e.g.

```bash
POSTGRES_PRISMA_URL=postgresql://postgres:postgres@localhost:5433/myapp
POSTGRES_URL_NON_POOLING=postgresql://postgres:postgres@localhost:5433/myapp
NEXT_PUBLIC_DSN=...
```

3. Initialize the database schema:

```bash
npx prisma migrate dev --name init
```

4. Seed the database with initial data:

```bash
npx prisma db seed
```

## Deploy

See [../README.md](../README.md)
