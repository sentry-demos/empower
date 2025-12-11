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
        if (request?.Cart == null)
        {
            return BadRequest(new { status = "failed", error = "Invalid checkout request: missing cart" });
        }

        var validateInventory = !string.Equals(request.ValidateInventory, "false", StringComparison.OrdinalIgnoreCase);
        var quantities = ParseQuantities(request.Cart.Quantities);

        if (validateInventory && quantities.Count == 0)
        {
            return BadRequest(new { status = "failed", error = "Invalid checkout request: cart is empty" });
        }

        if (!validateInventory)
        {
            _logger.LogInformation("Checkout succeeded without inventory validation");
            return Ok(new { status = "success" });
        }

        var productIds = quantities.Keys.ToList();

        var inventorySpan = SentrySdk.GetSpan()?.StartChild("checkout.get_inventory", "function");
        var inventory = await _dbContext.Inventory
            .Where(item => item.ProductId != null && productIds.Contains(item.ProductId.Value))
            .ToListAsync();
        inventorySpan?.Finish();

        var inventoryByProduct = inventory
            .Where(item => item.ProductId.HasValue)
            .ToDictionary(item => item.ProductId!.Value, item => item);

        var fulfilledCount = 0;
        var outOfStock = new List<string>();

        foreach (var entry in quantities)
        {
            var productId = entry.Key;
            var requestedQuantity = entry.Value;
            var availableQuantity = inventoryByProduct.TryGetValue(productId, out var inventoryItem)
                ? inventoryItem.Count
                : 0;

            if (availableQuantity >= requestedQuantity)
            {
                fulfilledCount++;
                inventoryItem!.Count -= requestedQuantity;
            }
            else
            {
                outOfStock.Add(request.Cart.GetTitleForProduct(productId));
            }
        }

        object payload;
        if (outOfStock.Count == 0)
        {
            payload = new { status = "success" };
            _logger.LogInformation("Checkout succeeded for {ProductCount} products", quantities.Count);
        }
        else if (fulfilledCount == 0)
        {
            payload = new { status = "failed", out_of_stock = outOfStock };
            _logger.LogWarning("Checkout failed; out of stock for {Products}", string.Join(", ", outOfStock));
        }
        else
        {
            payload = new { status = "partial", out_of_stock = outOfStock };
            _logger.LogWarning("Checkout partially fulfilled; out of stock for {Products}", string.Join(", ", outOfStock));
        }

        return Ok(payload);
    }

    private static Dictionary<int, int> ParseQuantities(Dictionary<string, int>? quantities)
    {
        var parsed = new Dictionary<int, int>();
        if (quantities == null)
        {
            return parsed;
        }

        foreach (var entry in quantities)
        {
            if (int.TryParse(entry.Key, out var productId) && entry.Value > 0)
            {
                parsed[productId] = entry.Value;
            }
        }

        return parsed;
    }

    public class CheckoutRequest
    {
        [JsonPropertyName("cart")]
        public CartRequest? Cart { get; set; }

        [JsonPropertyName("form")]
        public Dictionary<string, object?>? Form { get; set; }

        [JsonPropertyName("validate_inventory")]
        public string? ValidateInventory { get; set; }
    }

    public class CartRequest
    {
        [JsonPropertyName("items")]
        public List<CartItem> Items { get; set; } = new();

        [JsonPropertyName("quantities")]
        public Dictionary<string, int>? Quantities { get; set; }

        [JsonPropertyName("total")]
        public decimal? Total { get; set; }

        public string GetTitleForProduct(int productId)
        {
            return Items?.FirstOrDefault(item => item.Id == productId)?.Title ?? $"Product #{productId}";
        }
    }

    public class CartItem
    {
        [JsonPropertyName("id")]
        public int Id { get; set; }

        [JsonPropertyName("title")]
        public string? Title { get; set; }
    }
}
