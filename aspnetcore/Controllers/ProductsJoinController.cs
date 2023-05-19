namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class ProductsJoinController : ControllerBase
{
    [HttpGet]
    public string Get() => "aspnetcore /products-join";
}
