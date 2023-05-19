namespace Empower.Backend;

/// <summary>
/// This is custom middleware used in this app.
/// It sets Sentry tags and user info based on incoming request headers, for every request in the app.
/// </summary>
public class AppMiddleware
{
    private readonly RequestDelegate _next;

    public AppMiddleware(RequestDelegate next)
    {
        _next = next;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        var headers = context.Request.Headers;
        
        var se = (string?) headers["se"];
        var customerType = (string?) headers["customerType"];
        var email = (string?) headers["email"];

        SentrySdk.ConfigureScope(scope =>
        {
            if (se is not null)
            {
                scope.SetTag("se", se);
            }

            if (customerType is not null)
            {
                scope.SetTag("customerType", customerType);
            }

            if (email is not null)
            {
                scope.User = new User
                {
                    Email = email
                };
            }
        });

        await _next(context);
    }
}