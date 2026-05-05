namespace Empower.Backend.Controllers;

[ApiController]
[Route("product/0/info")]
public class ProductInfoController : ControllerBase
{
    private readonly ILogger<ProductInfoController> _logger;

    public ProductInfoController(ILogger<ProductInfoController> logger)
    {
        _logger = logger;
    }

    [HttpGet]
    public string Get([FromQuery] int? id = null)
    {
        _logger.LogInformation("Received /product/0/info endpoint request (id={Id})", id);
        return "aspnetcore /product/0/info";
    }
}

// Thrown when ?in_stock_only=1 hits /products — typed for distinct Sentry grouping.
public class InventoryUnavailableException : Exception
{
    public InventoryUnavailableException(string message) : base(message) { }
}
