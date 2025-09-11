Empower Go backend (Flask parity)

Endpoints mirror `flask/src/main.py` with intentional delays and quirks preserved. Uses net/http, pgx, Redis, asynq, Sentry, Statsig, and OpenAI placeholder.

Local run: env is provided by top-level `deploy.sh --env=local go` which calls `run.sh`.

Required env (see `validate_env.list`):
- GO_APP_DSN, GO_ENV, GO_RELEASE
- GO_RUBY_BACKEND
- GO_REDISHOST, GO_LOCAL_REDISPORT
- DB_HOST, DB_DATABASE, DB_USERNAME, DB_PASSWORD, DB_CLOUD_SQL_CONNECTION_NAME
- OPENAI_API_KEY (optional), STATSIG_SERVER_KEY

