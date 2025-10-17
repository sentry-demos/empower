namespace Empower.Backend.Models;

public class CheckoutRequest
{
    public required Cart Cart { get; set; }
    public required CustomerForm Form { get; set; }
    public string? ValidateInventory { get; set; }
}

public class Cart
{
    public required Dictionary<string, int> Quantities { get; set; }
    public required List<CartItem> Items { get; set; }
}

public class CartItem
{
    public required int Id { get; set; }
    public required string Title { get; set; }
    public required string Description { get; set; }
    public required int Price { get; set; }
    public required string Img { get; set; }
    public required int Quantity { get; set; }
}

public class CustomerForm
{
    public required string Email { get; set; }
    public required string FirstName { get; set; }
    public required string LastName { get; set; }
    public required string Address { get; set; }
    public required string City { get; set; }
    public required string Country { get; set; }
    public required string State { get; set; }
    public required string Zipcode { get; set; }
}

public class CheckoutResponse
{
    public required string Status { get; set; }
    public List<string>? OutOfStock { get; set; }
}