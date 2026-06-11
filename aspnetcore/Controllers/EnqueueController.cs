namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class EnqueueController : ControllerBase
{
    private readonly IEmailQueue _queue;
    private readonly ILogger<EnqueueController> _logger;

    public EnqueueController(IEmailQueue queue, ILogger<EnqueueController> logger)
    {
        _queue = queue;
        _logger = logger;
    }

    public class EnqueueBody
    {
        public string? Email { get; set; }
    }

    [HttpPost]
    public async Task<IActionResult> Post([FromBody] EnqueueBody body)
    {
        if (body is null || string.IsNullOrWhiteSpace(body.Email))
        {
            return BadRequest(new { error = "email is required" });
        }

        // Wrap the enqueue in a child span so the trace shows queue.send before the
        // worker's queue.process transaction. Capture sentry-trace + baggage from the
        // current span so the worker can continue this trace.
        var span = SentrySdk.GetSpan()?.StartChild("queue.send", "email.welcome");
        span?.SetData("messaging.system", "in-process-channel");
        span?.SetData("messaging.destination.name", "email");

        // Capture the current trace header + baggage so the worker can continue this trace.
        var sentryTrace = SentrySdk.GetTraceHeader()?.ToString();
        var baggage = SentrySdk.GetBaggage()?.ToString();

        await _queue.EnqueueAsync(new EmailTask(
            Email: body.Email,
            SentryTrace: sentryTrace,
            Baggage: baggage,
            EnqueuedAt: DateTimeOffset.UtcNow));

        span?.Finish();

        _logger.LogInformation("Enqueued welcome email for {Email}", body.Email);
        return Accepted(new { status = "enqueued", email = body.Email });
    }
}
