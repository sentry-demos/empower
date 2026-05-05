Demo ASP.NET Core 9 HTTP service

Uses the controller-based Web API approach.
See https://learn.microsoft.com/aspnet/core/web-api

1. Install the latest .NET 9 SDK from https://dotnet.microsoft.com/download
   - Use the OS and architecture that matches your machine.
   - For example, choose Arm64 if you have an Apple Silicon (M1+) machine, or x64 if you have an Intel processor.

```
./deploy --env=local aspnetcore
```

Open in browser: http://localhost:8091/products

## Run locally with front end:

```
./deploy --env=local aspnetcore react
```

Open in browser: http://localhost:3000/?backend=aspnetcore

## Run locally without the deploy script

The `./deploy` flow pulls config from GCP Secret Manager. For contributors who
don't have GCP access, you can wire things up by hand:

1. Start Postgres (the seed file is auto-loaded from `_postgres/data/empowerplant.sql`):

   ```
   docker compose up -d postgres
   ```

2. Create `aspnetcore/.env` (template is `_.env.template`):

   ```
   ASPNETCORE_RELEASE=local
   ASPNETCORE_DSN=<your Sentry DSN — leave empty to run without Sentry>
   ASPNETCORE_LOCAL_PORT=8091
   BACKEND_URL_RUBYONRAILS=http://localhost:8082
   DB_DATABASE=postgres
   DB_HOST=localhost
   DB_USERNAME=postgres
   DB_PASSWORD=postgres
   ```

   Note: the seed loads tables into the default `postgres` database, not
   `hardwarestore` — the script doesn't have a `CREATE DATABASE` line.

3. Build and run:

   ```
   cd aspnetcore
   dotnet build -c Release
   ./run_local.sh
   ```

## Demo endpoints

Each endpoint intentionally exercises a different Sentry feature. Hit them
locally to see issues / transactions land in your project.

| Method | Path          | Behavior                                                                 |
|--------|---------------|--------------------------------------------------------------------------|
| GET    | `/products`   | Returns products + reviews; calls Rails service for header-propagated trace |
| GET    | `/products-join` | Same data via JOIN query                                              |
| GET    | `/reviews`    | Returns all reviews                                                      |
| POST   | `/checkout`   | Always throws `OutOfInventoryException` ("Not enough inventory")        |
| GET    | `/handled`    | Triggers a `FormatException`, captures it manually, returns `"failed"`  |
| GET    | `/unhandled`  | Throws `KeyNotFoundException` (no local catch)                           |
| GET    | `/api`        | Health-style endpoint, returns `"aspnetcore /api"`                       |
| GET    | `/organization`, `/connect`, `/success` | Simple stub responses                          |

Notes:
- Every DB query is artificially delayed 1–3 seconds (`DemoCommandInterceptor`)
  to make traces interesting in Sentry.
- The header tags `se`, `customerType`, `email` are read off each request and
  attached to the Sentry scope (see `AppMiddleware`).
- The Rails inter-service call from `/products` is best-effort — if Rails is
  down, the failure is captured to Sentry but the request still returns 200.

## PII handling

PII scrubbing is wired at SDK initialization in `Program.cs` via Sentry's
`SetBeforeSend` and `SetBeforeBreadcrumb` hooks; the actual scrub logic lives
in `PiiScrubber.cs`. This is the first line of defense — Sentry's project-level
data scrubbing rules are the second.

**What's scrubbed:**
- `Authorization`, `Cookie`, `Set-Cookie`, `X-API-Key` headers → `[Filtered]`
- Credit-card-shape numbers (13–19 digits) anywhere in event strings → `[CARD_REDACTED]`
- JSON-style values for keys named `password`, `ssn`, `secret`, `api_key`,
  `apikey`, `token` → `[REDACTED]`
- Auto-attached IPs / cookies (`SendDefaultPii = false`)

**What's intentionally preserved:**
- `user.email` — set deliberately by `AppMiddleware` from the `email` request
  header to identify SE/customer demo scenarios. Filtering by user is itself a
  Sentry feature this demo showcases.
- `se`, `customerType` tags — same reason.

To verify scrubbing locally, hit `/checkout` with a payload containing a card
number and a `password` field while sending an `Authorization` header. The
event in Sentry will show all three masked.

## Deploy to production:
**(requires ASPNETCORE_APP_ENGINE_SERVICE=application-monitoring-aspnetcore in env-config/production.env)**

```
./deploy --env=production aspnetcore
```
