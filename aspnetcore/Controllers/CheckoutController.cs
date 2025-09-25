namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class CheckoutController : ControllerBase
{
    private readonly HardwareStoreContext _context;
    private readonly ILogger<CheckoutController> _logger;

    public CheckoutController(HardwareStoreContext context, ILogger<CheckoutController> logger)
    {
        _context = context;
        _logger = logger;
    }

    [HttpPost]
    public async Task<ActionResult<CheckoutResponse>> Checkout([FromBody] CheckoutRequest request)
    {
        _logger.LogInformation("Received /checkout endpoint request");

        var cart = request.Cart;
        var form = request.Form;
        var validateInventory = string.IsNullOrEmpty(request.ValidateInventory) || request.ValidateInventory == "true";

        _logger.LogInformation("Processing /checkout - validating order details");

        // Get inventory for all products in cart
        var productIds = cart.Quantities.Keys.Select(int.Parse).ToList();
        
        List<Inventory> inventory;
        try
        {
            inventory = await _context.Inventory
                .Where(i => productIds.Contains(i.ProductId ?? 0))
                .ToListAsync();
        }
        catch (Exception err)
        {
            _logger.LogError(err, "Failed to get inventory");
            throw;
        }

        var fulfilledCount = 0;
        var outOfStock = new List<string>();

        try
        {
            if (validateInventory)
            {
                var quantities = cart.Quantities.ToDictionary(kv => int.Parse(kv.Key), kv => kv.Value);
                
                if (!quantities.Any())
                {
                    return BadRequest(new { error = "Invalid checkout request: cart is empty" });
                }

                var inventoryDict = inventory.ToDictionary(x => x.ProductId ?? 0, x => x);

                foreach (var productId in quantities.Keys)
                {
                    var inventoryCount = inventoryDict.ContainsKey(productId) ? inventoryDict[productId].Count : 0;
                    if (inventoryCount >= quantities[productId])
                    {
                        // In a real implementation, you would decrement inventory here
                        // DecrementInventory(inventoryDict[productId].Id, quantities[productId]);
                        fulfilledCount++;
                    }
                    else
                    {
                        var title = cart.Items.FirstOrDefault(x => x.Id == productId)?.Title ?? "Unknown Product";
                        outOfStock.Add(title);
                    }
                }
            }
        }
        catch (Exception err)
        {
            _logger.LogError(err, "Failed to validate inventory with cart: {Cart}", cart);
            return BadRequest(new { error = "Error validating enough inventory for product" });
        }

        if (!outOfStock.Any())
        {
            _logger.LogInformation("Checkout successful");
            return Ok(new CheckoutResponse { Status = "success" });
        }
        else
        {
            // React doesn't handle these yet, shows "Checkout complete" as long as it's HTTP 200
            if (fulfilledCount == 0)
            {
                return Ok(new CheckoutResponse { Status = "failed" }); // All items are out of stock
            }
            else
            {
                return Ok(new CheckoutResponse { Status = "partial", OutOfStock = outOfStock });
            }
        }
    }
}
