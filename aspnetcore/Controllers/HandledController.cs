namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class HandledController : ControllerBase
{
    [HttpGet]
    public string Get() => "aspnetcore /handled";
}
