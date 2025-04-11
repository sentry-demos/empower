namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class CheckoutController : ControllerBase
{
    private readonly HardwareStoreContext _context;

    public class CheckoutRequest
    {
        public Cart Cart { get; set; }
        public object Form { get; set; }
        public string Validate_inventory { get; set; }
    }

    public class Cart
    {
        public List<CartItem> Items { get; set; }
        public Dictionary<string, int> Quantities { get; set; }
        public decimal Total { get; set; }
    }

    public class CartItem
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public string Sku { get; set; }
    }

    public CheckoutController(HardwareStoreContext context)
    {
        _context = context;
    }

    [HttpPost]
    public async Task<IActionResult> Checkout([FromBody] CheckoutRequest request)
    {
        if (request.Validate_inventory?.ToLower() == "false")
        {
            return Ok(new { success = true, message = "Order processed successfully" });
        }

        bool hasInsufficientInventory = false;
        string insufficientItem = "";

        if (request.Cart?.Items != null && request.Cart.Quantities != null)
        {
            foreach (var item in request.Cart.Items)
            {
                if (request.Cart.Quantities.TryGetValue(item.Id.ToString(), out int quantity))
                {
                    var inventory = await _context.Set<Inventory>()
                        .FirstOrDefaultAsync(i => i.ProductId == item.Id || i.Sku == item.Sku);

                    if (inventory == null || inventory.Count < quantity)
                    {
                        hasInsufficientInventory = true;
                        insufficientItem = item.Name;
                        break;
                    }
                }
            }
        }

        if (hasInsufficientInventory)
        {
            throw new Exception($"Not enough inventory for {insufficientItem}");
        }

        return Ok(new { success = true, message = "Order processed successfully" });
    }
}
