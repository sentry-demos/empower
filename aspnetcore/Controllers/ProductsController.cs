namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class ProductsController : ControllerBase
{
    private readonly HardwareStoreContext _dbContext;
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly ILogger<ProductsController> _logger;
    private readonly string? _rubyBackendBaseUrl;

    public ProductsController(
        HardwareStoreContext dbContext,
        IHttpClientFactory httpClientFactory,
        ILogger<ProductsController> logger)
    {
        _dbContext = dbContext;
        _httpClientFactory = httpClientFactory;
        _logger = logger;
        _rubyBackendBaseUrl = Environment.GetEnvironmentVariable("BACKEND_URL_RUBYONRAILS");
    }

    [HttpGet]
    public async Task<IList<Product>> Get(
        [FromQuery] string? fetch_promotions = null,
        [FromQuery] string? in_stock_only = null)
    {
        // Strings (not bools) — React sends ?in_stock_only=1 which the bool binder rejects.
        var fetchPromotions = IsTruthy(fetch_promotions);
        var inStockOnly = IsTruthy(in_stock_only);

        _logger.LogInformation(
            "Received /products endpoint request (fetch_promotions={FetchPromotions}, in_stock_only={InStockOnly})",
            fetchPromotions, inStockOnly);

        var products = await GetProductsAsync();

        if (inStockOnly)
        {
            throw new InventoryUnavailableException("Inventory data unavailable");
        }

        if (fetchPromotions)
        {
            ScanDescriptionsForPests(products);
        }

        // Awaited (not .Wait()) so exceptions surface as their real type, not AggregateException.
        await CallHttpApiAsync();

        return products;
    }

    private static bool IsTruthy(string? value)
    {
        if (string.IsNullOrEmpty(value)) return false;
        return value != "0" && !string.Equals(value, "false", StringComparison.OrdinalIgnoreCase);
    }

    private void ScanDescriptionsForPests(List<Product> products)
    {
        var span = SentrySdk.GetSpan()?.StartChild("code.block", "products.scan_descriptions");
        var startedAt = DateTimeOffset.UtcNow;

        // CPU-bound work to give the profiler something to show on the slow path.
        var pests = new[] { "fungus", "aphid", "blight", "mite", "mold" };
        var hits = 0;
        for (var iter = 0; iter < 2000; iter++)
        {
            foreach (var product in products)
            {
                var description = product.DescriptionFull ?? product.Description ?? string.Empty;
                foreach (var pest in pests)
                {
                    if (description.Contains(pest, StringComparison.OrdinalIgnoreCase))
                    {
                        hits++;
                    }
                }
            }
        }

        span?.SetData("scan.iterations", 2000);
        span?.SetData("scan.hits", hits);
        span?.SetData("duration_ms", (DateTimeOffset.UtcNow - startedAt).TotalMilliseconds);
        span?.Finish();
    }

    private async Task<List<Product>> GetProductsAsync()
    {
        var span = SentrySdk.GetSpan()?.StartChild("code.block", "products.get_products");
        var startedAt = DateTimeOffset.UtcNow;

        var products = await _dbContext.Products
            .Include(e => e.Reviews)
            .ToListAsync();

        if (span is not null)
        {
            span.SetData("products.count", products.Count);
            span.SetData("reviews.count", products.Sum(p => p.Reviews?.Count ?? 0));
            span.SetData("duration_ms", (DateTimeOffset.UtcNow - startedAt).TotalMilliseconds);
        }

        SentrySdk.Metrics.EmitDistribution("products.fetched", products.Count);
        SentrySdk.Metrics.EmitDistribution("products.fetch_duration_ms",
            (DateTimeOffset.UtcNow - startedAt).TotalMilliseconds);

        span?.Finish();

        return products;
    }

    private async Task CallHttpApiAsync()
    {
        // Best-effort call to demonstrate cross-service tracing — failure is captured but doesn't fail the request.
        var span = SentrySdk.GetSpan()?.StartChild("code.block", "api_request");
        var url = _rubyBackendBaseUrl + "/api";
        var startedAt = DateTimeOffset.UtcNow;

        // Set up-front so failed-call spans still carry context.
        span?.SetData("http.method", "GET");
        span?.SetData("http.url", url);

        try
        {
            // SendAsync inside the try so connection failures land in the catch too.
            var request = new HttpRequestMessage(HttpMethod.Get, url);
            request.CopyHeadersFrom(Request.Headers, "se", "customerType", "email");

            var httpClient = _httpClientFactory.CreateClient();
            var response = await httpClient.SendAsync(request);
            span?.SetData("http.status_code", (int)response.StatusCode);
            span?.SetData("duration_ms", (DateTimeOffset.UtcNow - startedAt).TotalMilliseconds);
            response.EnsureSuccessStatusCode();
            span?.Finish();
        }
        catch (Exception exception)
        {
            span?.SetData("duration_ms", (DateTimeOffset.UtcNow - startedAt).TotalMilliseconds);
            span?.Finish(exception);

            SentrySdk.CaptureException(exception, scope =>
            {
                scope.Contexts["downstream_http"] = new Dictionary<string, object>
                {
                    ["url"] = url,
                    ["method"] = "GET",
                    ["service"] = "ruby-on-rails",
                    ["error_type"] = exception.GetType().FullName ?? exception.GetType().Name,
                    ["duration_ms"] = (DateTimeOffset.UtcNow - startedAt).TotalMilliseconds,
                };
            });
        }
    }
}
