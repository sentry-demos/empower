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
        var cart = body.GetProperty("cart");
        var validateInventory = true;
        if (body.TryGetProperty("validate_inventory", out var vi))
        {
            validateInventory = vi.GetString() != "false";
        }

        if (validateInventory)
        {
            var quantities = cart.GetProperty("quantities");
            var productIds = new List<int>();
            foreach (var prop in quantities.EnumerateObject())
            {
                productIds.Add(int.Parse(prop.Name));
            }

            var inventory = await _dbContext.Inventory
                .Where(i => productIds.Contains(i.ProductId ?? 0))
                .ToListAsync();

            var inventoryDict = inventory
                .Where(i => i.ProductId.HasValue)
                .ToDictionary(i => i.ProductId!.Value);

            foreach (var prop in quantities.EnumerateObject())
            {
                var productId = int.Parse(prop.Name);
                var requested = prop.Value.GetInt32();
                var available = inventoryDict.TryGetValue(productId, out var inv) ? inv.Count : 0;
                if (available < requested)
                {
                    throw new Exception("Not enough inventory for product");
                }
            }
        }

        return Ok(new { status = "success" });
    }
}
