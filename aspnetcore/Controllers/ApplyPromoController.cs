namespace Empower.Backend.Controllers;

// POST /apply-promo-code — Flask parity (flask/src/main.py:apply_promo_code).
// React's CheckoutForm posts { value: "<code>" } here and expects:
//   400 missing value · 404 not found · 410 expired (yes, 410) · 200 { success, promo_code }
[ApiController]
[Route("apply-promo-code")]
public class ApplyPromoController : ControllerBase
{
    private readonly HardwareStoreContext _dbContext;
    private readonly ILogger<ApplyPromoController> _logger;

    public ApplyPromoController(HardwareStoreContext dbContext, ILogger<ApplyPromoController> logger)
    {
        _dbContext = dbContext;
        _logger = logger;
    }

    public class ApplyPromoBody
    {
        [JsonPropertyName("value")]
        public string? Value { get; set; }
    }

    [HttpPost]
    public async Task<IActionResult> Post([FromBody] ApplyPromoBody body)
    {
        _logger.LogInformation("[/apply-promo-code] request received");

        var promoCode = body?.Value?.Trim();

        if (string.IsNullOrEmpty(promoCode))
        {
            _logger.LogWarning("[/apply-promo-code] bad request - missing value parameter");
            return BadRequest();
        }

        var promo = await GetPromoCodeAsync(promoCode);

        if (promo is null)
        {
            _logger.LogWarning("[/apply-promo-code] code not found: {Code}", promoCode);
            SentrySdk.Metrics.EmitCounter("promo.apply", 1,
                [new KeyValuePair<string, object>("result", "not_found")]);
            return NotFound(new
            {
                error = new { code = "not_found", message = "Promo code not found." }
            });
        }

        // expires_at in the past → 410 Gone (matches Flask's deliberately tricky status code).
        if (promo.ExpiresAt.HasValue && promo.ExpiresAt.Value <= DateTime.Now)
        {
            _logger.LogWarning("[/apply-promo-code] code has expired: {Code}", promoCode);
            SentrySdk.Metrics.EmitCounter("promo.apply", 1,
                [new KeyValuePair<string, object>("result", "expired")]);
            return StatusCode(StatusCodes.Status410Gone, new
            {
                error = new { code = "expired", message = "Provided coupon code has expired." }
            });
        }

        _logger.LogInformation("[/apply-promo-code] valid code found: {Code}", promoCode);
        SentrySdk.Metrics.EmitCounter("promo.apply", 1,
            [new KeyValuePair<string, object>("result", "applied")]);

        return Ok(new
        {
            success = true,
            promo_code = new
            {
                code = promo.Code,
                percent_discount = promo.PercentDiscount,
                max_dollar_savings = promo.MaxDollarSavings,
            }
        });
    }

    // Mirrors flask's get_promo_code: a traced lookup with explicit connect + query
    // child spans, so the promo path reads the same across stacks in Sentry.
    private async Task<PromoCode?> GetPromoCodeAsync(string code)
    {
        var span = SentrySdk.GetSpan()?.StartChild("db.query", "get_promo_code");
        try
        {
            var promo = await _dbContext.PromoCodes
                .FirstOrDefaultAsync(p => p.Code == code && p.IsActive == true);

            span?.SetData("promo_code", promo?.Code ?? "none");
            span?.Finish();
            return promo;
        }
        catch (Exception exception)
        {
            span?.Finish(exception);
            throw;
        }
    }
}
