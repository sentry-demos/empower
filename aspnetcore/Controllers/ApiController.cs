namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class ApiController : ControllerBase
{
    [HttpGet]
    public string Get() => "aspnetcore /api";
}
