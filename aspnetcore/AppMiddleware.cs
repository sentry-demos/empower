namespace Empower.Backend;

// Reads request headers (se, customerType, email, cexp) and stamps them onto
// the Sentry scope so every event from this request carries them.
public class AppMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<AppMiddleware> _logger;

    public AppMiddleware(RequestDelegate next, ILogger<AppMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        _logger.LogInformation("Running custom middleware.");

        var headers = context.Request.Headers;

        // StringValues casts to "" (not null) when missing — use IsNullOrEmpty, not `is not null`.
        // React's fetch wrapper sends the literal string "undefined" when ?se= is omitted; treat
        // that as absent so it doesn't become a real tag value (matches Flask's behavior).
        var se = (string?) headers["se"];
        var customerType = (string?) headers["customerType"];
        var email = (string?) headers["email"];
        var cexp = (string?) headers["cexp"];

        SentrySdk.ConfigureScope(scope =>
        {
            if (IsRealValue(se)) scope.SetTag("se", se!);
            if (IsRealValue(customerType)) scope.SetTag("customerType", customerType!);
            if (IsRealValue(cexp)) scope.SetTag("cexp", cexp!);
            if (IsRealValue(email)) scope.User = new SentryUser { Email = email };
        });

        await _next(context);
    }

    private static bool IsRealValue(string? value) =>
        !string.IsNullOrEmpty(value) && value != "undefined";
}
