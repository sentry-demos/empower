using Sentry.Extensibility;
using DotNetEnv;

Env.Load();

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        options.JsonSerializerOptions.ReferenceHandler = ReferenceHandler.IgnoreCycles;
        options.JsonSerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
    });

builder.Services.AddCors(options => options.AddDefaultPolicy(policy => policy
    .AllowAnyOrigin()
    .AllowAnyHeader()
    .AllowAnyMethod()));

// The slow-query interceptor reads ?slow from the current request, so it needs the accessor.
builder.Services.AddHttpContextAccessor();

builder.Services.AddDbContext<HardwareStoreContext>((sp, options) =>
{
    var connectionString = AppUtils.GetConnectionString(builder.Configuration);
    options.UseNpgsql(connectionString);
    options.AddInterceptors(new DemoCommandInterceptor(sp.GetRequiredService<IHttpContextAccessor>()));
});

builder.WebHost.UseSentry(options =>
{
    var dsn = Environment.GetEnvironmentVariable("ASPNETCORE_DSN");
    if (!string.IsNullOrEmpty(dsn))
    {
        options.Dsn = dsn;
    }

    options.Release = Environment.GetEnvironmentVariable("ASPNETCORE_RELEASE");

    // Map Development/Staging/Production to local/staging/production so cross-backend filters work.
    options.Environment = builder.Environment.EnvironmentName.ToLowerInvariant() switch
    {
        "development" => "local",
        var name => name,
    };

    options.DefaultTags["backendType"] = "aspnetcore";

    options.TracesSampleRate = 1.0;
    options.AutoSessionTracking = true;

    // Drop OPTIONS preflights, otherwise stamp method/path onto scope so issues show why a transaction was sampled.
    options.TracesSampler = samplingContext =>
    {
        string? method = null;
        string? path = null;

        if (samplingContext.CustomSamplingContext.TryGetValue("HttpContext", out var ctx)
            && ctx is HttpContext httpContext)
        {
            method = httpContext.Request.Method;
            path = httpContext.Request.Path.Value;
        }

        if (string.IsNullOrEmpty(method))
        {
            var name = samplingContext.TransactionContext.Name ?? string.Empty;
            var spaceIdx = name.IndexOf(' ');
            if (spaceIdx > 0)
            {
                method = name[..spaceIdx];
                path = name[(spaceIdx + 1)..];
            }
        }

        var isOptions = !string.IsNullOrEmpty(method) && HttpMethods.IsOptions(method);
        double? decision = isOptions ? 0.0 : null;

        SentrySdk.ConfigureScope(scope =>
        {
            scope.Contexts["sampling_context"] = new Dictionary<string, object?>
            {
                ["http.method"] = method,
                ["http.path"] = path,
                ["decision"] = isOptions ? "drop (OPTIONS preflight)" : "keep (TracesSampleRate=1.0)",
            };
        });

        return decision;
    };

    options.SendDefaultPii = false;

    if (builder.Environment.IsDevelopment())
    {
        options.Debug = true;
    }

    options.CaptureBlockingCalls = true;
    options.MaxRequestBodySize = RequestSize.Always;
    options.StackTraceMode = StackTraceMode.Enhanced;
    options.AttachStacktrace = true;

    // Mark our own assembly's frames as "in-app" so Sentry highlights them and the
    // "App Only" toggle collapses framework/Sentry frames. This is the difference between
    // a wall of runtime internals and a stack trace that points straight at YOUR code.
    options.AddInAppInclude("Empower");

    options.EnableLogs = true;
    options.EnableMetrics = true;
    options.AddIntegration(new Sentry.Profiling.ProfilingIntegration(TimeSpan.FromMilliseconds(500)));
    options.ProfilesSampleRate = 1.0;

    // ILogger.LogError shouldn't auto-create Sentry events; we capture explicitly where we want them.
    options.MinimumEventLevel = LogLevel.None;
    options.MinimumBreadcrumbLevel = LogLevel.Information;

    options.SetBeforeSendLog(log =>
    {
        string? email = null;
        SentrySdk.ConfigureScope(scope => email = scope.User?.Email);
        if (!string.IsNullOrEmpty(email))
        {
            log.SetAttribute("user.email", email);
        }
        return log;
    });

    options.SetBeforeSend((sentryEvent, hint) =>
    {
        // Blocking-call detection (CaptureBlockingCalls=true) also fires on framework-
        // internal locks — e.g. Sentry's profiler emitting a Debug log through the
        // synchronous console sink. Those events have NO in-app frame, so they point at
        // runtime internals a customer can't act on. Drop them so "Blocking call detected"
        // only surfaces blocks that happen in our own code (see GET /blocking).
        var isBlockingCall = sentryEvent.SentryExceptions?
            .Any(e => string.Equals(e.Mechanism?.Type, "BlockingCallDetector", StringComparison.Ordinal)) ?? false;
        if (isBlockingCall &&
            !sentryEvent.SentryExceptions!
                .SelectMany(e => e.Stacktrace?.Frames ?? Enumerable.Empty<SentryStackFrame>())
                .Any(f => f.InApp == true))
        {
            return null;
        }

        IssueFingerprinter.Fingerprint(sentryEvent);
        PiiScrubber.Scrub(sentryEvent);
        return sentryEvent;
    });

    options.SetBeforeBreadcrumb((breadcrumb, hint) => PiiScrubber.Scrub(breadcrumb));

    // Transactions carry request body separately from events — needs its own scrub hook.
    options.SetBeforeSendTransaction((transaction, hint) =>
    {
        PiiScrubber.ScrubRequest(transaction.Request);
        return transaction;
    });
});

builder.Services.AddHttpClient();

// In-memory cache + a Sentry-instrumented wrapper. Emitting cache.get/cache.put
// spans is what lights up Sentry > Insights > Caches for this service (the .NET
// SDK doesn't auto-instrument caches the way the Python SDK does).
builder.Services.AddMemoryCache();
builder.Services.AddSingleton<SentryCache>();

// Periodic Sentry cron check-ins for the "demo-job-aspnetcore" monitor.
builder.Services.AddHostedService<CheckInHostedService>();

// In-process Channel-backed email queue + background consumer. Demonstrates
// Sentry trace propagation from HTTP request -> background worker via ContinueTrace.
builder.Services.AddSingleton<IEmailQueue, ChannelEmailQueue>();
builder.Services.AddHostedService<EmailWorkerHostedService>();

var app = builder.Build();

app.UseMiddleware<AppMiddleware>();
app.UseCors();

// Capture to Sentry before swallowing — without this the catch hides errors from Sentry's diagnostic listener.
app.Use(async (context, next) =>
{
    try
    {
        await next();
    }
    catch (Exception ex)
    {
        SentrySdk.CaptureException(ex);

        // Append, not Add — Add throws if header is already set upstream.
        context.Response.Headers.Append("Access-Control-Allow-Origin", "*");
        context.Response.StatusCode = 500;
        context.Response.ContentType = "application/json";
        await context.Response.WriteAsJsonAsync(new { error = "Internal Server Error" });
    }
});

app.UseSentryTracing();
app.MapControllers();

app.Run();
