namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class CheckoutController : ControllerBase
{
    [HttpPost]
    public void Checkout() => throw new Exception("Not enough inventory for product");
}
