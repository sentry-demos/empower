namespace Empower.Backend.Controllers;

// Deliberate N+1 pattern: one query to load all products, then a per-product
// query for reviews. Sentry's Performance Issue detector should flag this as
// "N+1 Query" in the trace. Compare with /products (uses .Include).
[ApiController]
[Route("products-n1")]
public class ProductsN1Controller : ControllerBase
{
    private readonly HardwareStoreContext _dbContext;
    private readonly ILogger<ProductsN1Controller> _logger;

    public ProductsN1Controller(HardwareStoreContext dbContext, ILogger<ProductsN1Controller> logger)
    {
        _dbContext = dbContext;
        _logger = logger;
    }

    [HttpGet]
    public async Task<IList<Product>> Get()
    {
        _logger.LogInformation("Received /products-n1 endpoint request (intentional N+1)");

        var listSpan = SentrySdk.GetSpan()?.StartChild("db.query", "products.list_without_reviews");
        var products = await _dbContext.Products.AsNoTracking().ToListAsync();
        listSpan?.SetData("products.count", products.Count);
        listSpan?.Finish();

        // The bad part — one round-trip per product instead of a single JOIN.
        var loopSpan = SentrySdk.GetSpan()?.StartChild("code.block", "products.fetch_reviews_per_product");
        loopSpan?.SetData("queries", products.Count);

        foreach (var product in products)
        {
            var perProductSpan = SentrySdk.GetSpan()?.StartChild("db.query", "reviews.by_product_id");
            perProductSpan?.SetData("product.id", product.Id);

            var reviews = await _dbContext.Reviews
                .AsNoTracking()
                .Where(r => r.ProductId == product.Id)
                .ToListAsync();

            product.Reviews = reviews;

            perProductSpan?.SetData("reviews.count", reviews.Count);
            perProductSpan?.Finish();
        }

        loopSpan?.Finish();
        return products;
    }
}
