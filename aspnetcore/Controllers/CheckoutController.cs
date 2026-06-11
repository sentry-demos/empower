namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class CheckoutController : ControllerBase
{
    [HttpPost]
    public async Task Checkout()
    {
        SentrySdk.AddBreadcrumb("Checkout request received", category: "checkout");

        // Cart validation step
        var validateSpan = SentrySdk.GetSpan()?.StartChild("code.block", "checkout.validate_cart");
        await Task.Delay(20);
        validateSpan?.SetData("cart.items", 3);
        validateSpan?.SetData("cart.total", 42.99);
        validateSpan?.Finish();

        SentrySdk.AddBreadcrumb("Cart validated, 3 items", category: "checkout");

        // Inventory check (always insufficient — demo path)
        var inventorySpan = SentrySdk.GetSpan()?.StartChild("code.block", "checkout.check_inventory");
        await Task.Delay(50);
        inventorySpan?.SetData("inventory.status", "insufficient");
        inventorySpan?.SetData("inventory.shortfall", 2);
        inventorySpan?.Finish();

        // Attach cart context onto scope so the captured event surfaces it as a "Cart" panel.
        SentrySdk.ConfigureScope(scope =>
        {
            scope.Contexts["cart"] = new Dictionary<string, object>
            {
                ["items"] = 3,
                ["total"] = 42.99,
                ["currency"] = "USD",
                ["promo_code"] = "none",
            };
        });

        SentrySdk.AddBreadcrumb(
            "Inventory insufficient — failing checkout",
            level: BreadcrumbLevel.Warning,
            category: "checkout");

        SentrySdk.Metrics.EmitCounter("checkout.received", 1);
        SentrySdk.Metrics.EmitCounter("checkout.failed", 1);

        throw new OutOfInventoryException("Not enough inventory");
    }
}

public class OutOfInventoryException : Exception
{
    public OutOfInventoryException(string message) : base(message) { }
}
