using Empower.Backend;
using System.Collections.Generic;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Sentry;
using System;
using System.Threading.Tasks;

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
        bool validateInventory = request.Validate_inventory?.ToLower() == "true";

        if (validateInventory)
        {
            using var transaction = await _dbContext.Database.BeginTransactionAsync();
            try
            {
                foreach (var item in request.Cart.Items)
                {
                    var inventory = await _dbContext.Inventory.FirstOrDefaultAsync(i => i.ProductId == item.Id);
                    if (inventory == null || inventory.Count < item.Quantity)
                    {
                        await transaction.RollbackAsync();
                        return BadRequest($"Not enough inventory for product ID: {item.Id}");
                    }
                    inventory.Count -= item.Quantity;
                }
                await _dbContext.SaveChangesAsync();
                await transaction.CommitAsync();
            }
            catch (Exception ex)
            {
                await transaction.RollbackAsync();
                SentrySdk.CaptureException(ex);
                return StatusCode(500, "An unexpected error occurred during checkout.");
            }
        }
        return Ok("Checkout successful.");
    }
}

public class CheckoutRequest
{
    public Cart Cart { get; set; }
    public Form Form { get; set; }
    public string Validate_inventory { get; set; }
}

public class Cart
{
    public List<CartItem> Items { get; set; }
    public decimal Total { get; set; }
}

public class CartItem
{
    public int Id { get; set; }
    public int Quantity { get; set; }
}

public class Form
{
    public string Email { get; set; }
    public string FirstName { get; set; }
    public string LastName { get; set; }
    public string Address { get; set; }
    public string City { get; set; }
    public string Country { get; set; }
    public string State { get; set; }
    public string ZipCode { get; set; }
}
