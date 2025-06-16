namespace Empower.Backend.Models;

public class ProductInCart 
{ 
    public int Id { get; set; } 
}

public class CartDto 
{ 
    public Dictionary<string, int> Quantities { get; set; } = new Dictionary<string, int>();
    public List<ProductInCart> Items { get; set; } = new List<ProductInCart>();
    public decimal Total { get; set; } 
}

public class FormDto 
{ 
    public string Email { get; set; } = string.Empty;
    public string Subscribe { get; set; } = string.Empty;
    public string FirstName { get; set; } = string.Empty;
    public string LastName { get; set; } = string.Empty;
    public string Address { get; set; } = string.Empty;
    public string City { get; set; } = string.Empty;
    public string Country { get; set; } = string.Empty;
    public string State { get; set; } = string.Empty;
    public string ZipCode { get; set; } = string.Empty;
}

public class CheckoutRequest 
{ 
    public CartDto Cart { get; set; } = new CartDto();
    public FormDto Form { get; set; } = new FormDto();
    public string Validate_Inventory { get; set; } = string.Empty;
}