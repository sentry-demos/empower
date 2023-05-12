namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class OrganizationController : ControllerBase
{
    [HttpGet]
    public string Get() => "aspnetcore /organization";
}
