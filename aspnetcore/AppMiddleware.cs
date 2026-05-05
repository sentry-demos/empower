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
        var se = (string?) headers["se"];
        var customerType = (string?) headers["customerType"];
        var email = (string?) headers["email"];
        var cexp = (string?) headers["cexp"];

        SentrySdk.ConfigureScope(scope =>
        {
            if (!string.IsNullOrEmpty(se)) scope.SetTag("se", se);
            if (!string.IsNullOrEmpty(customerType)) scope.SetTag("customerType", customerType);
            if (!string.IsNullOrEmpty(cexp)) scope.SetTag("cexp", cexp);
            if (!string.IsNullOrEmpty(email)) scope.User = new SentryUser { Email = email };
        });

        await _next(context);
    }
}
