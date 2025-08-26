namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class CheckoutController : ControllerBase
{
    private readonly HardwareStoreContext _dbContext;

    public CheckoutController(HardwareStoreContext dbContext)
    {
        _dbContext = dbContext;
    }

    [HttpPost]
    public async Task<IActionResult> Checkout([FromBody] CheckoutRequest request)
    {
        try
        {
            // Simulate processing time (like in other controllers)
            await Task.Delay(TimeSpan.FromMilliseconds(Random.Shared.Next(100, 500)));

            // Default to validating inventory unless explicitly set to false
            var validateInventory = request.ValidateInventory != "false";

            if (request.Cart?.Quantities == null || !request.Cart.Quantities.Any())
            {
                return BadRequest(new { status = "failed", error = "Cart is empty" });
            }

            var outOfStock = new List<string>();
            var fulfilledCount = 0;

            if (validateInventory)
            {
                // Get inventory for all products in cart
                var productIds = request.Cart.Quantities.Keys.Select(int.Parse).ToList();
                var inventoryItems = await _dbContext.Inventory
                    .Where(i => productIds.Contains(i.ProductId.Value))
                    .ToListAsync();

                var inventoryDict = inventoryItems.ToDictionary(i => i.ProductId.Value, i => i);

                // Check inventory for each product
                foreach (var cartItem in request.Cart.Quantities)
                {
                    var productId = int.Parse(cartItem.Key);
                    var requestedQuantity = cartItem.Value;

                    if (inventoryDict.TryGetValue(productId, out var inventoryItem))
                    {
                        if (inventoryItem.Count >= requestedQuantity)
                        {
                            // Sufficient inventory - would decrement here in real implementation
                            fulfilledCount++;
                        }
                        else
                        {
                            // Not enough inventory
                            var product = request.Cart.Items?.FirstOrDefault(p => p.Id == productId);
                            var productTitle = product?.Title ?? $"Product {productId}";
                            outOfStock.Add(productTitle);
                        }
                    }
                    else
                    {
                        // Product not found in inventory
                        var product = request.Cart.Items?.FirstOrDefault(p => p.Id == productId);
                        var productTitle = product?.Title ?? $"Product {productId}";
                        outOfStock.Add(productTitle);
                    }
                }
            }
            else
            {
                // If not validating inventory, assume all items are fulfilled
                fulfilledCount = request.Cart.Quantities.Count;
            }

            // Determine response based on fulfillment
            if (outOfStock.Count == 0)
            {
                return Ok(new { status = "success" });
            }
            else if (fulfilledCount == 0)
            {
                return Ok(new { status = "failed", out_of_stock = outOfStock });
            }
            else
            {
                return Ok(new { status = "partial", out_of_stock = outOfStock });
            }
        }
        catch (Exception ex)
        {
            // Log the exception and return an error response
            return StatusCode(500, new { status = "error", message = "An error occurred during checkout" });
        }
    }
}

public class CheckoutRequest
{
    public CartData? Cart { get; set; }
    public FormData? Form { get; set; }
    public string? ValidateInventory { get; set; }
}

public class CartData
{
    public Dictionary<string, int>? Quantities { get; set; }
    public List<CartItem>? Items { get; set; }
    public decimal? Total { get; set; }
}

public class CartItem
{
    public int Id { get; set; }
    public string? Title { get; set; }
    public decimal? Price { get; set; }
    public string? Img { get; set; }
}

public class FormData
{
    public string? Email { get; set; }
    public string? Subscribe { get; set; }
    public string? FirstName { get; set; }
    public string? LastName { get; set; }
    public string? Address { get; set; }
    public string? City { get; set; }
    public string? Country { get; set; }
    public string? State { get; set; }
    public string? ZipCode { get; set; }
}
