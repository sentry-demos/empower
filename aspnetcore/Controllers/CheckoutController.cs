namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class CheckoutController : ControllerBase
{
    [HttpPost]
    public void Checkout()
    {
        // Metrics fire before the throw so the always-failing demo path still records them.
        SentrySdk.Metrics.EmitCounter("checkout.received", 1);
        SentrySdk.Metrics.EmitCounter("checkout.failed", 1);

        throw new OutOfInventoryException("Not enough inventory");
    }
}

// Typed so Sentry groups checkout failures distinctly from generic Exceptions.
public class OutOfInventoryException : Exception
{
    public OutOfInventoryException(string message) : base(message) { }
}
