namespace Empower.Backend.Models;

public class CheckoutRequest
{
    public required Dictionary<string, int> Items { get; set; } // SKU -> Quantity
}