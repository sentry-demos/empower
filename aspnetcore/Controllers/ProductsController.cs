namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class ProductsController : ControllerBase
{
    private readonly HardwareStoreContext _dbContext;
    private readonly IHttpClientFactory _httpClientFactory;
    private readonly string _rubyBackendBaseUrl;

    public ProductsController(HardwareStoreContext dbContext, IHttpClientFactory httpClientFactory)
    {
        _dbContext = dbContext;
        _httpClientFactory = httpClientFactory;
        _rubyBackendBaseUrl = Environment.GetEnvironmentVariable("RUBY_BACKEND") ??
                              "https://application-monitoring-ruby-dot-sales-engineering-sf.appspot.com";
    }

    [HttpGet]
    public async Task<IList<Product>> Get()
    {
        var products = await GetProductsAsync();
        
        await CallHttpApiAsync();
        
        return products;
    }

    private async Task<List<Product>> GetProductsAsync()
    {
        var span = SentrySdk.GetSpan()?.StartChild("/products.get_products", "function");
        
        var products = await _dbContext.Products
            .Include(e => e.Reviews)
            .ToListAsync();

        CloseDbConnectionSpan();
        
        span?.Finish();
        
        return products;
    }

    private static void CloseDbConnectionSpan()
    {
        // Workaround for https://github.com/getsentry/sentry-dotnet/issues/2372
        var span = SentrySdk.GetSpan();
        if (span?.Operation == "db.connection")
        {
            span.Finish();
        }
    }

    private async Task CallHttpApiAsync()
    {
        // NOTE: This is just here to demonstrate calling another service with HTTP and collecting spans accordingly.
        // It doesn't actually do anything with the result unless there's a failure response code.

        var span = SentrySdk.GetSpan()?.StartChild("/api_request", "function");
        
        var request = new HttpRequestMessage(HttpMethod.Get, _rubyBackendBaseUrl + "/api");
        request.CopyHeadersFrom(Request.Headers, "se", "customerType", "email");
        
        var httpClient = _httpClientFactory.CreateClient();
        var response = await httpClient.SendAsync(request);

        try
        {
            response.EnsureSuccessStatusCode();
        }
        catch (Exception exception)
        {
            SentrySdk.CaptureException(exception);
        }

        span?.Finish();
    }
}
