using Empower.Backend.Models;

namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class CheckoutController : ControllerBase
{
    private readonly HardwareStoreContext _context;

    public CheckoutController(HardwareStoreContext context)
    {
        _context = context;
    }

    [HttpPost]
    public async Task<IActionResult> Checkout([FromBody] CheckoutRequest request, [FromQuery] bool? v2)
    {
        try
        {
            // Start Sentry tracing
            using var transaction = SentrySdk.StartTransaction("checkout", "http.request");
            SentrySdk.ConfigureScope(scope => scope.Transaction = transaction);

            bool shouldValidateInventory = "true".Equals(request.Validate_Inventory, StringComparison.OrdinalIgnoreCase);

            if (shouldValidateInventory)
            {
                // Loop through cart items and validate inventory
                foreach (var cartItem in request.Cart.Quantities)
                {
                    if (!int.TryParse(cartItem.Key, out int productId))
                    {
                        return BadRequest(new { message = $"Invalid product ID: {cartItem.Key}" });
                    }

                    var inventory = await _context.Inventory.FirstOrDefaultAsync(i => i.ProductId == productId);
                    if (inventory == null)
                    {
                        return BadRequest(new { message = $"Product not found: {productId}" });
                    }

                    if (inventory.Count < cartItem.Value)
                    {
                        return Conflict(new { message = $"Not enough inventory for product {productId}. Available: {inventory.Count}, Requested: {cartItem.Value}" });
                    }
                }
            }

            // If validation passes or is skipped, return success
            return Ok(new { message = "Checkout successful!" });
        }
        catch (Exception ex)
        {
            SentrySdk.CaptureException(ex);
            return StatusCode(500, new { message = "Internal server error during checkout" });
        }
    }
}
