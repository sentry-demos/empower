namespace Empower.Backend.Controllers;

[ApiController]
public class CronController : ControllerBase
{
    private const string ManualMonitorSlug = "demo-job-aspnetcore-manual";

    private readonly ILogger<CronController> _logger;

    public CronController(ILogger<CronController> logger)
    {
        _logger = logger;
    }

    [HttpGet("cron-ok")]
    public IActionResult CronOk()
    {
        var id = SentrySdk.CaptureCheckIn(
            ManualMonitorSlug,
            CheckInStatus.Ok,
            duration: TimeSpan.FromMilliseconds(120),
            configureMonitorOptions: ConfigureManualMonitor);

        _logger.LogInformation("Manual cron OK check-in {Id}", id);
        return Ok(new { status = "ok", checkInId = id.ToString(), monitorSlug = ManualMonitorSlug });
    }

    [HttpGet("cron-fail")]
    public IActionResult CronFail()
    {
        var id = SentrySdk.CaptureCheckIn(
            ManualMonitorSlug,
            CheckInStatus.Error,
            duration: TimeSpan.FromMilliseconds(450),
            configureMonitorOptions: ConfigureManualMonitor);

        _logger.LogWarning("Manual cron ERROR check-in {Id}", id);
        return StatusCode(200, new { status = "error", checkInId = id.ToString(), monitorSlug = ManualMonitorSlug });
    }

    private static void ConfigureManualMonitor(SentryMonitorOptions opts)
    {
        opts.Interval(5, SentryMonitorInterval.Minute);
        opts.CheckInMargin = TimeSpan.FromMinutes(1);
        opts.MaxRuntime = TimeSpan.FromMinutes(2);
        opts.FailureIssueThreshold = 1;
    }
}
