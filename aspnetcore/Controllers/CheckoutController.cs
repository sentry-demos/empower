using System.Text.Json;

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
    public async Task<IActionResult> Checkout([FromBody] JsonElement body)
    {
        var validateInventory = true;
        if (body.TryGetProperty("validate_inventory", out var vi))
        {
            validateInventory = vi.GetString() == "true";
        }

        var inventory = await _dbContext.Inventory.ToListAsync();

        if (validateInventory)
        {
            if (body.TryGetProperty("cart", out var cart) &&
                cart.TryGetProperty("quantities", out var quantities))
            {
                var inventoryDict = inventory.ToDictionary(i => i.ProductId ?? 0, i => i.Count);

                foreach (var prop in quantities.EnumerateObject())
                {
                    var productId = int.Parse(prop.Name);
                    var requestedQty = prop.Value.GetInt32();
                    var availableCount = inventoryDict.GetValueOrDefault(productId, 0);

                    if (availableCount < requestedQty)
                    {
                        throw new Exception($"Not enough inventory for product: {productId}");
                    }
                }
            }
        }

        return Ok(new { status = "success" });
    }
}
