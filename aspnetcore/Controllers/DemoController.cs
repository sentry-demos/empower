namespace Empower.Backend.Controllers;

// One-stop cheat sheet for SE / customer demos. Lists every demo endpoint,
// which Sentry SKU it exercises, and a curl example. Hit `GET /demo` to read
// it back during a call: `curl -s http://localhost:8091/demo | jq`.
[ApiController]
[Route("[controller]")]
public class DemoController : ControllerBase
{
    public class Demo
    {
        public required string Sku { get; init; }
        public required string Method { get; init; }
        public required string Path { get; init; }
        public required string Description { get; init; }
        public required string ExpectInSentry { get; init; }
        public string? Curl { get; init; }
    }

    [HttpGet]
    public IActionResult Get()
    {
        var orgSlug = Environment.GetEnvironmentVariable("SENTRY_ORG_SLUG") ?? "demo";
        var projectSlug = "backend-aspnetcore";
        var projectId = TryGetProjectIdFromDsn();
        var baseSentryUrl = $"https://{orgSlug}.sentry.io";

        var demos = new[]
        {
            new Demo {
                Sku = "Errors (unhandled)",
                Method = "GET", Path = "/unhandled",
                Description = "Throws KeyNotFoundException — no catch.",
                ExpectInSentry = "New issue in backend-aspnetcore, level=error, stack trace into UnhandledController.Get.",
                Curl = "curl http://localhost:8091/unhandled",
            },
            new Demo {
                Sku = "Errors (handled)",
                Method = "GET", Path = "/handled",
                Description = "Catches FormatException, captures via SentrySdk.CaptureException.",
                ExpectInSentry = "Issue with level=error, marked handled. Endpoint returns 200 'failed'.",
                Curl = "curl http://localhost:8091/handled",
            },
            new Demo {
                Sku = "Errors + Custom Fingerprinting",
                Method = "POST", Path = "/checkout",
                Description = "Always throws OutOfInventoryException. Custom fingerprint applied via IssueFingerprinter.",
                ExpectInSentry = "Issue grouped under a stable fingerprint matching Flask/React; breadcrumbs (cart validated, inventory insufficient); cart context panel.",
                Curl = "curl -X POST -H 'Content-Type: application/json' -d '{\"cart\":{\"items\":[{\"id\":3,\"qty\":2}]}}' http://localhost:8091/checkout",
            },
            new Demo {
                Sku = "Performance / Tracing",
                Method = "GET", Path = "/products",
                Description = "Loads products + reviews via JOIN, scans descriptions, calls Rails for cross-service trace. DB queries run at real speed by default; add ?slow=true (or ?slow=<ms>) to simulate a slow query.",
                ExpectInSentry = "Transaction with code.block spans (get_products, scan_descriptions, api_request). DB query span. http.client span to Rails (Rails server span joins if Rails is running).",
                Curl = "curl 'http://localhost:8091/products?slow=true'",
            },
            new Demo {
                Sku = "Performance Issue: N+1 query",
                Method = "GET", Path = "/products-n1",
                Description = "Deliberate N+1: fetches reviews in a per-product loop instead of with .Include. Use ?slow=true so each per-product query is slow enough to trip Sentry's N+1 detector.",
                ExpectInSentry = "Transaction with N similar reviews.by_product_id spans. Sentry surfaces this as 'N+1 Query' under Performance Issues.",
                Curl = "curl 'http://localhost:8091/products-n1?slow=true'",
            },
            new Demo {
                Sku = "Caches (Insights)",
                Method = "GET", Path = "/products",
                Description = "Cache-aside via SentryCache (IMemoryCache wrapper). Emits cache.get (cache.hit) + cache.put (cache.item_size) spans. First call after a 30s TTL misses (add ?slow=true to make the backing DB query slow and show the cache's value); subsequent calls hit. The .NET SDK does NOT auto-instrument caches — these spans are emitted manually to the Caches span convention.",
                ExpectInSentry = "Insights > Caches lists backend-aspnetcore (like flask/laravel): hit rate, throughput, avg item size. cache.get spans sliceable by cache.hit. Hit avoids the get_products db.query span entirely.",
                Curl = "curl 'http://localhost:8091/products?slow=true' && curl 'http://localhost:8091/products?slow=true'  # 1st miss (slow DB), 2nd hit (fast)",
            },
            new Demo {
                Sku = "Profiling",
                Method = "GET", Path = "/products?fetch_promotions=1",
                Description = "Runs CPU-bound description scan to generate a profile.",
                ExpectInSentry = "Profile attached to the transaction (Profiles tab). Flamegraph shows ScanDescriptionsForPests as hot.",
                Curl = "curl 'http://localhost:8091/products?fetch_promotions=1'",
            },
            new Demo {
                Sku = "Sentry Logs",
                Method = "GET", Path = "/handled",
                Description = "Calls ILogger.LogInformation and ILogger.LogError. EnableLogs=true ships them to Sentry Logs.",
                ExpectInSentry = "Log entries visible under Explore > Logs, scoped to the transaction's trace_id, with user.email attribute (added in BeforeSendLog).",
                Curl = "curl http://localhost:8091/handled",
            },
            new Demo {
                Sku = "Metrics",
                Method = "POST", Path = "/checkout",
                Description = "All 3 metric types via SentrySdk.Metrics: counters checkout.received{result}/checkout.failed{reason}, distributions checkout.order_total(usd)/checkout.order_items. /products adds products.* distributions; POST /enqueue emits the queue.email.depth gauge; /product/0/info emits product.info.viewed{product_id}.",
                ExpectInSentry = "Metrics: counters (sliceable by result/reason), distributions checkout.order_total + products.fetch_duration_ms(ms), gauge queue.email.depth. Tags appear as filterable dimensions.",
                Curl = "curl -X POST http://localhost:8091/checkout",
            },
            new Demo {
                Sku = "Crons (auto, periodic)",
                Method = "(background)", Path = "demo-job-aspnetcore",
                Description = "CheckInHostedService emits InProgress→Ok check-ins every minute. Monitor is auto-upserted via configureMonitorOptions.",
                ExpectInSentry = $"Crons > demo-job-aspnetcore. See 1-minute interval cadence of Ok check-ins. View at {baseSentryUrl}/crons/.",
                Curl = "(no curl — runs automatically)",
            },
            new Demo {
                Sku = "Crons (manual demo trigger)",
                Method = "GET", Path = "/cron-ok and /cron-fail",
                Description = "On-demand check-ins for demo-job-aspnetcore-manual (skip the wait).",
                ExpectInSentry = "/cron-fail produces a failing check-in; after FailureIssueThreshold (1) Sentry opens an issue.",
                Curl = "curl http://localhost:8091/cron-ok && curl http://localhost:8091/cron-fail",
            },
            new Demo {
                Sku = "Background worker / queue tracing",
                Method = "POST", Path = "/enqueue",
                Description = "Enqueues a welcome-email task; worker processes asynchronously and continues the same Sentry trace via SentrySdk.ContinueTrace.",
                ExpectInSentry = "Single trace spans POST /Enqueue (HTTP) + queue.process_email (worker). 10% chance of worker-side issue.",
                Curl = "curl -X POST -H 'Content-Type: application/json' -d '{\"email\":\"newsletter@example.com\"}' http://localhost:8091/enqueue",
            },
            new Demo {
                Sku = "Promo code lookup (DB + parity)",
                Method = "POST", Path = "/apply-promo-code",
                Description = "Flask-parity promo lookup. Posts {value}, queries promo_codes (get_promo_code span). 400 missing, 404 unknown, 410 expired, 200 applied. promo_codes is unseeded by default, so any code returns 404 until rows are inserted.",
                ExpectInSentry = "Transaction POST /apply-promo-code with a get_promo_code db.query span. promo.apply counter sliceable by result (applied/not_found/expired).",
                Curl = "curl -X POST -H 'Content-Type: application/json' -d '{\"value\":\"SAVE20\"}' http://localhost:8091/apply-promo-code",
            },
            new Demo {
                Sku = "User Feedback",
                Method = "POST", Path = "/feedback",
                Description = "Captures user feedback via SentrySdk.CaptureFeedback.",
                ExpectInSentry = $"User Feedback > new entry with name/email/message. View at {baseSentryUrl}/feedback/.",
                Curl = "curl -X POST -H 'Content-Type: application/json' -d '{\"name\":\"Demo User\",\"email\":\"demo@example.com\",\"message\":\"The plant stroller scared my cat!\"}' http://localhost:8091/feedback",
            },
            new Demo {
                Sku = "Release Health / Sessions",
                Method = "(automatic)", Path = "(every request)",
                Description = "AutoSessionTracking=true sends session events. Release tag = ASPNETCORE_RELEASE env var.",
                ExpectInSentry = "Releases > <release> > crash-free sessions/users.",
            },
            new Demo {
                Sku = "PII / Data Scrubbing",
                Method = "POST", Path = "/checkout",
                Description = "Send sensitive headers + body. PiiScrubber filters them.",
                ExpectInSentry = "Authorization=[Filtered], password=[REDACTED], card number=[CARD_REDACTED] in the event payload.",
                Curl = "curl -X POST -H 'Authorization: Bearer secret' -H 'Content-Type: application/json' -d '{\"password\":\"hunter2\",\"card\":\"4111111111111111\"}' http://localhost:8091/checkout",
            },
            new Demo {
                Sku = "Blocking-call detection",
                Method = "GET", Path = "/blocking",
                Description = "Deliberate sync-over-async (Task.Delay(500).Wait()) on the request thread. CaptureBlockingCalls=true flags it; AddInAppInclude(\"Empower\") marks the frame in-app.",
                ExpectInSentry = "'Blocking call detected' whose stack trace points at Controllers/BlockingController.cs (in-app, with source) — not framework internals. Framework-only blocking calls are dropped in BeforeSend. Fix = await instead of .Wait().",
                Curl = "curl http://localhost:8091/blocking",
            },
        };

        return Ok(new
        {
            org = orgSlug,
            project = projectSlug,
            projectId,
            sentry = baseSentryUrl,
            issuesUrl = projectId is not null ? $"{baseSentryUrl}/issues/?project={projectId}&environment=local" : null,
            tracesUrl = projectId is not null ? $"{baseSentryUrl}/explore/traces/?project={projectId}&environment=local" : null,
            logsUrl = projectId is not null ? $"{baseSentryUrl}/explore/logs/?project={projectId}&environment=local" : null,
            cronsUrl = $"{baseSentryUrl}/crons/",
            feedbackUrl = $"{baseSentryUrl}/feedback/",
            demos,
        });
    }

    // The DSN path component is the numeric project ID. Used to build deep links.
    private static string? TryGetProjectIdFromDsn()
    {
        var dsn = Environment.GetEnvironmentVariable("ASPNETCORE_DSN");
        if (string.IsNullOrEmpty(dsn)) return null;
        if (!Uri.TryCreate(dsn, UriKind.Absolute, out var uri)) return null;
        var path = uri.AbsolutePath.Trim('/');
        return string.IsNullOrEmpty(path) ? null : path;
    }
}
