namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class UnhandledController : ControllerBase
{
    [HttpGet]
    public string Get() => "aspnetcore /unhandled";
}
