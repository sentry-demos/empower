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

        // Metrics — each type answers a different question; tags make them sliceable.
        //   Counter      → how often does this happen? (broken down by outcome)
        //   Distribution → what's the shape? (avg/sum + p50/p90/p99 of value & size)
        SentrySdk.Metrics.EmitCounter("checkout.received", 1,
            [new KeyValuePair<string, object>("result", "failed")]);

        // Order shape. Mirrors flask's "checkout.captured.revenue" and
        // react's "checkout_submit.order_total" / "num_items".
        SentrySdk.Metrics.EmitDistribution("checkout.order_total", 42.99,
            MeasurementUnit.Custom("usd"),
            [new KeyValuePair<string, object>("currency", "USD")]);
        SentrySdk.Metrics.EmitDistribution("checkout.order_items", 3);

        // Failures broken down by reason → a dashboard can show WHY checkout fails.
        SentrySdk.Metrics.EmitCounter("checkout.failed", 1,
            [new KeyValuePair<string, object>("reason", "insufficient_inventory")]);

        throw new OutOfInventoryException("Not enough inventory");
    }
}

public class OutOfInventoryException : Exception
{
    public OutOfInventoryException(string message) : base(message) { }
}
