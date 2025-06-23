using Empower.Backend.Models;
using Microsoft.EntityFrameworkCore;

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
        using (var transaction = await _dbContext.Database.BeginTransactionAsync())
        {
            try
            {
                // Check if inventory validation is required
                if (request.Validate_inventory != "false")
                {
                    // Check inventory for each item in cart
                    foreach (var cartItem in request.Cart.Items)
                    {
                        var inventory = await _dbContext.Inventory
                            .FirstOrDefaultAsync(i => i.ProductId == cartItem.Id);
                        
                        if (inventory == null || inventory.Count < cartItem.Quantity)
                        {
                            throw new Exception($"Not enough inventory for product {cartItem.Title}");
                        }
                    }

                    // Update inventory by decrementing stock
                    foreach (var cartItem in request.Cart.Items)
                    {
                        var inventory = await _dbContext.Inventory
                            .FirstOrDefaultAsync(i => i.ProductId == cartItem.Id);
                        
                        if (inventory != null)
                        {
                            inventory.Count -= cartItem.Quantity;
                        }
                    }
                }

                // Create order
                var order = new Order
                {
                    OrderDate = DateTime.UtcNow,
                    Total = request.Cart.Total
                };

                _dbContext.Orders.Add(order);
                await _dbContext.SaveChangesAsync();
                await transaction.CommitAsync();

                return Ok(new { orderId = order.Id });
            }
            catch (Exception ex)
            {
                await transaction.RollbackAsync();
                SentrySdk.CaptureException(ex);
                return StatusCode(500, new { message = ex.Message });
            }
        }
    }
}
