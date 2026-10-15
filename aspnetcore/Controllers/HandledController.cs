namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class HandledController : ControllerBase
{
    private readonly ILogger<HandledController> _logger;

    public HandledController(ILogger<HandledController> logger)
    {
        _logger = logger;
    }

    [HttpGet]
    public string Get()
    {
        _logger.LogInformation("Received /handled endpoint request");

        try
        {
            int.Parse("not-a-number");  // intentional throw for the demo
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Processing /handled - intentional exception occurred");
            SentrySdk.CaptureException(ex);
        }

        return "failed";
    }
}
