namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class SuccessController : ControllerBase
{
    [HttpGet]
    public string Get() => "aspnetcore /success";
}
