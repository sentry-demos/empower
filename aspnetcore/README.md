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
| GET    | `/products-n1` | Deliberate N+1 (no `.Include`, per-product review fetch) — surfaces as Performance Issue |
| GET    | `/reviews`    | Returns all reviews                                                      |
| POST   | `/checkout`   | Always throws `OutOfInventoryException` ("Not enough inventory")        |
| GET    | `/handled`    | Triggers a `FormatException`, captures it manually, returns `"failed"`  |
| GET    | `/unhandled`  | Throws `KeyNotFoundException` (no local catch)                           |
| POST   | `/enqueue`    | Puts a welcome-email task on an in-process Channel queue. Background `EmailWorkerHostedService` consumes it; trace continues from request into worker via `SentrySdk.ContinueTrace`. Matches Flask's Celery `/enqueue`. 10% simulated send failure produces a `queue.process` issue. |
| POST   | `/feedback`   | Captures user feedback via `SentrySdk.CaptureFeedback` (User Feedback SKU) |
| GET    | `/cron-ok`    | On-demand OK check-in for monitor `demo-job-aspnetcore-manual` (Crons SKU) |
| GET    | `/cron-fail`  | On-demand Error check-in for monitor `demo-job-aspnetcore-manual` (opens an issue at FailureIssueThreshold=1) |
| GET    | `/demo`       | JSON cheat sheet — every endpoint, the SKU it shows, expected Sentry behavior, curl example |
| GET    | `/api`        | Health-style endpoint, returns `"aspnetcore /api"`                       |
| GET    | `/organization`, `/connect`, `/success` | Simple stub responses                          |

Plus a background `CheckInHostedService` that emits InProgress→Ok check-ins
for `demo-job-aspnetcore` every minute (Crons SKU; monitor is auto-upserted
the first time it runs — no UI setup needed).

Notes:
- Every DB query is artificially delayed 1–3 seconds (`DemoCommandInterceptor`)
  to make traces interesting in Sentry.
- The header tags `se`, `customerType`, `email` are read off each request and
  attached to the Sentry scope (see `AppMiddleware`).
- The Rails inter-service call from `/products` is best-effort — if Rails is
  down, the failure is captured to Sentry but the request still returns 200.

## Customer demo cheat sheet

One-curl-per-SKU. Use these in front of a customer to show each Sentry
product. `GET /demo` returns the same map as JSON so you can `curl -s
http://localhost:8091/demo | jq` during a live call.

| Sentry SKU | One-liner | Where it lands in Sentry |
|---|---|---|
| **Errors (unhandled)** | `curl http://localhost:8091/unhandled` | Issues → new `KeyNotFoundException` |
| **Errors (handled)** | `curl http://localhost:8091/handled` | Issues → `FormatException`, level=error, handled=true |
| **Custom fingerprinting** | `curl -X POST http://localhost:8091/checkout` | Same fingerprint across Flask/React/.NET — see `IssueFingerprinter.cs` |
| **PII / data scrubbing** | `curl -X POST -H 'Authorization: Bearer secret' -d '{"password":"hunter2","card":"4111111111111111"}' -H 'Content-Type: application/json' http://localhost:8091/checkout` | Event payload shows `[Filtered]` / `[REDACTED]` / `[CARD_REDACTED]` |
| **Performance / Tracing** | `curl http://localhost:8091/products` | Traces → transaction with `code.block` + `db.query` + `http.client` spans |
| **Performance Issue: N+1** | `curl http://localhost:8091/products-n1` | Performance Issues → "N+1 Query" with repeated `reviews.by_product_id` spans |
| **Profiling** | `curl 'http://localhost:8091/products?fetch_promotions=1'` | Profile tab on the transaction, `ScanDescriptionsForPests` hot |
| **Sentry Logs** | `curl http://localhost:8091/handled` | Explore → Logs (filter `trace_id:<id>`); user.email attached |
| **Metrics** | `curl -X POST http://localhost:8091/checkout` | Counters: `checkout.received`, `checkout.failed`; Distribution: `products.fetched` |
| **Release Health** | (any request) | Releases → crash-free sessions/users for `ASPNETCORE_RELEASE` |
| **Crons (auto)** | (nothing — background service) | Crons → `demo-job-aspnetcore`, OK every minute |
| **Crons (manual)** | `curl http://localhost:8091/cron-ok` / `curl http://localhost:8091/cron-fail` | Crons → `demo-job-aspnetcore-manual`. Failure opens an issue. |
| **User Feedback** | `curl -X POST -H 'Content-Type: application/json' -d '{"name":"Demo","email":"demo@example.com","message":"the plant stroller scared my cat"}' http://localhost:8091/feedback` | User Feedback list in Sentry |
| **Background worker / queue tracing** | `curl -X POST -H 'Content-Type: application/json' -d '{"email":"newsletter@example.com"}' http://localhost:8091/enqueue` | Single trace spans `POST /Enqueue` (request) + `queue.process_email` (worker), connected via `ContinueTrace`. With ~10% chance produces a worker-side error issue. |
| **Distributed tracing across services** | start Rails + `curl http://localhost:8091/products` | Trace waterfall spans both `backend-aspnetcore` (server) and `backend-rubyonrails` (server) |

Out of scope on this backend (covered by other services in the repo): Session
Replay (frontend SDKs in `react/`, `angular/`, `vue/`), AI/Agent Monitoring
(`agent/`), Uptime Monitoring (configured in the Sentry UI, not SDK).

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
