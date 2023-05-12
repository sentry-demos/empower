namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class CheckoutController : ControllerBase
{
    [HttpPost]
    public void Checkout()
    {
        var se = (string?) Request.Headers["se"];
        var customerType = (string?) Request.Headers["customerType"];
        var email = (string?) Request.Headers["email"];

        SentrySdk.ConfigureScope(scope =>
        {
            if (se is not null)
            {
                scope.SetTag("se", se);
            }

            if (customerType is not null)
            {
                scope.SetTag("customerType", customerType);
            }

            if (email is not null)
            {
                scope.User = new User
                {
                    Email = email
                };
            }
        });

        throw new Exception("Not enough inventory");
    }
}
