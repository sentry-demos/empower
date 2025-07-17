namespace Empower.Backend.Controllers;

[ApiController]
[Route("products-join")]
public class ProductsJoinController : ControllerBase
{
    private readonly HardwareStoreContext _dbContext;

    public ProductsJoinController(HardwareStoreContext dbContext)
    {
        _dbContext = dbContext;
    }

    [HttpGet]
    public async Task<IList<Product>> Get()
    {
        var products = await GetProductsAsync();
        
        return products;
    }

    private async Task<List<Product>> GetProductsAsync()
    {
        var span = SentrySdk.GetSpan()?.StartChild("/products.get_products", "function");

        var products = await _dbContext.Products
            .Include(e => e.Reviews)
            .ToListAsync();

        span?.Finish();
        
        return products;
    }
}
