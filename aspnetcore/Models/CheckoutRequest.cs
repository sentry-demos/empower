namespace Empower.Backend.Models;

public class CheckoutRequest
{
    public Cart Cart { get; set; } = new Cart();
    public CheckoutForm Form { get; set; } = new CheckoutForm();
    public string? Validate_inventory { get; set; }
}

public class Cart
{
    public List<CartItem> Items { get; set; } = new List<CartItem>();
    public decimal Total { get; set; }
}

public class CartItem
{
    public int Id { get; set; }
    public string Title { get; set; } = string.Empty;
    public string Img { get; set; } = string.Empty;
    public decimal Price { get; set; }
    public int Quantity { get; set; }
}

public class CheckoutForm
{
    public string Email { get; set; } = string.Empty;
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;
    public string Address { get; set; } = string.Empty;
    public string City { get; set; } = string.Empty;
    public string Country { get; set; } = string.Empty;
    public string State { get; set; } = string.Empty;
    public string ZipCode { get; set; } = string.Empty;
}