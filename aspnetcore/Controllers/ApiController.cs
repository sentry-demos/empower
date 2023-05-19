namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class ApiController : ControllerBase
{
    private readonly SentryAspNetCoreOptions _sentryOptions;

    public ApiController(IOptions<SentryAspNetCoreOptions> sentryOptions)
    {
        _sentryOptions = sentryOptions.Value;
    }

    [HttpGet]
    public string Get() => $"aspnetcore /api DSN: {_sentryOptions.Dsn}";
}
