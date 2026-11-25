namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class CheckoutController : ControllerBase
{
    private readonly HardwareStoreContext _dbContext;
    private readonly ILogger<CheckoutController> _logger;

    public CheckoutController(HardwareStoreContext dbContext, ILogger<CheckoutController> logger)
    {
        _dbContext = dbContext;
        _logger = logger;
    }

    [HttpPost]
    public async Task<IActionResult> Checkout([FromBody] CheckoutRequest request)
    {
        _logger.LogInformation("Received /checkout endpoint request.");

        var cart = request.Cart;
        if (cart is null || cart.Quantities.Count == 0)
        {
            _logger.LogWarning("Invalid checkout request: the cart is empty.");
            return BadRequest(new CheckoutResult { Status = "failed" });
        }

        var inventory = await GetInventoryAsync(cart);

        // As in the other backends, the inventory check only runs when the client asks for it.
        var validateInventory = string.Equals(request.ValidateInventory ?? "true", "true",
            StringComparison.OrdinalIgnoreCase);

        if (!validateInventory)
        {
            _logger.LogInformation("Checkout successful (inventory validation skipped).");
            return Ok(new CheckoutResult { Status = "success" });
        }

        _logger.LogInformation("Processing /checkout - validating order details.");

        var span = SentrySdk.GetSpan()?.StartChild("checkout.process_order", "function");

        var inventoryCounts = inventory
            .GroupBy(e => e.ProductId!.Value)
            .ToDictionary(g => g.Key, g => g.Sum(e => e.Count));

        var fulfilledCount = 0;
        var outOfStock = new List<string>();

        foreach (var (productId, quantity) in cart.Quantities)
        {
            inventoryCounts.TryGetValue(productId, out var available);
            if (available >= quantity)
            {
                fulfilledCount++;
            }
            else
            {
                var title = cart.Items.FirstOrDefault(e => e.Id == productId)?.Title ?? $"product {productId}";
                outOfStock.Add(title);
            }
        }

        span?.Finish();

        if (outOfStock.Count == 0)
        {
            _logger.LogInformation("Checkout successful.");
            return Ok(new CheckoutResult { Status = "success" });
        }

        _logger.LogWarning("Not enough inventory for: {OutOfStock}", string.Join(", ", outOfStock));

        return Ok(new CheckoutResult
        {
            // The frontends treat any HTTP 200 as a completed checkout, so partially
            // fulfilled orders are reported in the response body rather than as an error.
            Status = fulfilledCount == 0 ? "failed" : "partial",
            OutOfStock = outOfStock
        });
    }

    private async Task<List<Inventory>> GetInventoryAsync(Cart cart)
    {
        var span = SentrySdk.GetSpan()?.StartChild("/checkout.get_inventory", "function");

        var productIds = cart.Quantities.Keys.Select(id => (int?) id).ToList();

        var inventory = await _dbContext.Inventory
            .Where(e => productIds.Contains(e.ProductId))
            .ToListAsync();

        span?.Finish();

        return inventory;
    }
}

public class CheckoutRequest
{
    public Cart? Cart { get; set; }

    [JsonPropertyName("validate_inventory")]
    public string? ValidateInventory { get; set; }
}

public class Cart
{
    public List<CartItem> Items { get; set; } = new();

    public Dictionary<int, int> Quantities { get; set; } = new();
}

public class CartItem
{
    public int Id { get; set; }

    public string? Title { get; set; }
}

public class CheckoutResult
{
    public required string Status { get; set; }

    [JsonPropertyName("out_of_stock")]
    public List<string>? OutOfStock { get; set; }
}
