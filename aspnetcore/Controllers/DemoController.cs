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
                Description = "Loads products + reviews via JOIN, scans descriptions, calls Rails for cross-service trace.",
                ExpectInSentry = "Transaction with code.block spans (get_products, scan_descriptions, api_request). DB query span. http.client span to Rails (Rails server span joins if Rails is running).",
                Curl = "curl http://localhost:8091/products",
            },
            new Demo {
                Sku = "Performance Issue: N+1 query",
                Method = "GET", Path = "/products-n1",
                Description = "Deliberate N+1: fetches reviews in a per-product loop instead of with .Include.",
                ExpectInSentry = "Transaction with N similar reviews.by_product_id spans. Sentry surfaces this as 'N+1 Query' under Performance Issues.",
                Curl = "curl http://localhost:8091/products-n1",
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
                Description = "Emits checkout.received and checkout.failed counters via SentrySdk.Metrics.",
                ExpectInSentry = "Metrics > Counters: checkout.received, checkout.failed. Also Distribution metric products.fetched from /products.",
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
                Method = "GET", Path = "/products",
                Description = "CaptureBlockingCalls=true; any sync I/O on the request thread is flagged.",
                ExpectInSentry = "If sync I/O is present: 'Blocking call detected' performance issue on the transaction.",
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
