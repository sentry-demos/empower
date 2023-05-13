namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class ProductsController : ControllerBase
{
    private readonly HardwareStoreContext _dbContext;

    public ProductsController(HardwareStoreContext dbContext)
    {
        _dbContext = dbContext;
    }

    [HttpGet]
    public async Task<IList<Product>> Get() => await _dbContext.Products
        .Include(e => e.Reviews)
        .ToListAsync();
}
