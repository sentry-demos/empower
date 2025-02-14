using Microsoft.AspNetCore.Mvc;
using Empower.Backend.Models;
using Empower.Backend.Services;

namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class CheckoutController : ControllerBase
{
    private readonly InventoryService _inventoryService;

    public CheckoutController(InventoryService inventoryService)
    {
        _inventoryService = inventoryService;
    }

    [HttpPost]
    public async Task<IActionResult> Checkout([FromBody] CheckoutRequest request)
    {
        try
        {
            if (request.Items == null || !request.Items.Any())
            {
                return BadRequest("No items in checkout request");
            }

            var success = await _inventoryService.ValidateAndUpdateInventoryAsync(request.Items);
            
            return Ok(new { success = true, message = "Checkout completed successfully" });
        }
        catch (InvalidOperationException ex)
        {
            return BadRequest(new { success = false, message = ex.Message });
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { success = false, message = "An unexpected error occurred during checkout" });
        }
    }
}
