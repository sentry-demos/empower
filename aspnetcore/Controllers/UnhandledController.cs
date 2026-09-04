namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class UnhandledController : ControllerBase
{
    private readonly ILogger<UnhandledController> _logger;

    public UnhandledController(ILogger<UnhandledController> logger)
    {
        _logger = logger;
    }

    [HttpGet]
    public string Get()
    {
        _logger.LogInformation("Received /unhandled endpoint request");

        // Intentional KeyNotFoundException — Flask's KeyError equivalent.
        var data = new Dictionary<string, string>();
        return data["keyDoesntExist"];
    }
}
