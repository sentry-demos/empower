namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class ConnectController : ControllerBase
{
    [HttpGet]
    public string Get() => "aspnetcore /connect";
}
