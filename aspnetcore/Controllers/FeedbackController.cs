namespace Empower.Backend.Controllers;

[ApiController]
[Route("[controller]")]
public class FeedbackController : ControllerBase
{
    private readonly ILogger<FeedbackController> _logger;

    public FeedbackController(ILogger<FeedbackController> logger)
    {
        _logger = logger;
    }

    public class FeedbackBody
    {
        public string? Name { get; set; }
        public string? Email { get; set; }
        public string? Message { get; set; }
        public string? AssociatedEventId { get; set; }
        public string? Url { get; set; }
        public string? ReplayId { get; set; }
    }

    [HttpPost]
    public IActionResult Post([FromBody] FeedbackBody body)
    {
        if (body is null || string.IsNullOrWhiteSpace(body.Message))
        {
            return BadRequest(new { error = "message is required" });
        }

        // associatedEventId arrives as a string but the SDK wants SentryId? — parse defensively.
        SentryId? associatedEventId = null;
        if (!string.IsNullOrWhiteSpace(body.AssociatedEventId)
            && Guid.TryParse(body.AssociatedEventId, out var guid))
        {
            associatedEventId = new SentryId(guid);
        }

        var feedback = new SentryFeedback(
            message: body.Message,
            contactEmail: body.Email,
            name: body.Name,
            replayId: body.ReplayId,
            url: body.Url,
            associatedEventId: associatedEventId);

        SentrySdk.CaptureFeedback(feedback);

        _logger.LogInformation("Captured user feedback from {Email}", body.Email);

        return Ok(new { status = "captured" });
    }
}
