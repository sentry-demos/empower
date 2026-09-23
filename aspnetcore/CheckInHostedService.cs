namespace Empower.Backend;

// Periodic background worker that demos Sentry Cron monitoring.
// Sends InProgress → Ok check-ins for the "demo-job" monitor slug every minute.
// The configureMonitorOptions block upserts the monitor in Sentry the first time
// it runs, so you don't need to pre-create it in the UI.
public class CheckInHostedService : BackgroundService
{
    private const string MonitorSlug = "demo-job-aspnetcore";
    private static readonly TimeSpan Cadence = TimeSpan.FromMinutes(1);

    private readonly ILogger<CheckInHostedService> _logger;

    public CheckInHostedService(ILogger<CheckInHostedService> logger)
    {
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        // Stagger the first run so the SDK has settled.
        await Task.Delay(TimeSpan.FromSeconds(15), stoppingToken);

        while (!stoppingToken.IsCancellationRequested)
        {
            var checkInId = SentrySdk.CaptureCheckIn(
                MonitorSlug,
                CheckInStatus.InProgress,
                configureMonitorOptions: ConfigureMonitor);

            var startedAt = DateTimeOffset.UtcNow;
            try
            {
                // Stand-in for actual job work.
                await Task.Delay(TimeSpan.FromSeconds(2), stoppingToken);

                SentrySdk.CaptureCheckIn(
                    MonitorSlug,
                    CheckInStatus.Ok,
                    sentryId: checkInId,
                    duration: DateTimeOffset.UtcNow - startedAt);

                _logger.LogInformation("Cron check-in OK ({Slug})", MonitorSlug);
            }
            catch (Exception ex) when (ex is not OperationCanceledException)
            {
                SentrySdk.CaptureCheckIn(
                    MonitorSlug,
                    CheckInStatus.Error,
                    sentryId: checkInId,
                    duration: DateTimeOffset.UtcNow - startedAt);

                _logger.LogError(ex, "Cron check-in ERROR ({Slug})", MonitorSlug);
            }

            try
            {
                await Task.Delay(Cadence, stoppingToken);
            }
            catch (OperationCanceledException)
            {
                break;
            }
        }
    }

    private static void ConfigureMonitor(SentryMonitorOptions opts)
    {
        opts.Interval(1, SentryMonitorInterval.Minute);
        opts.CheckInMargin = TimeSpan.FromMinutes(1);
        opts.MaxRuntime = TimeSpan.FromMinutes(2);
        opts.FailureIssueThreshold = 2;
        opts.RecoveryThreshold = 2;
    }
}
