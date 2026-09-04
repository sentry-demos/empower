namespace Empower.Backend;

// Consumes EmailTask items off the in-process queue and "sends" the email
// (simulated). Each task continues the Sentry trace started by the enqueuing
// HTTP request via SentrySdk.ContinueTrace, so a single trace spans:
//   POST /enqueue (transaction) -> queue.send span -> queue.process transaction (this)
public class EmailWorkerHostedService : BackgroundService
{
    private readonly IEmailQueue _queue;
    private readonly ILogger<EmailWorkerHostedService> _logger;

    public EmailWorkerHostedService(IEmailQueue queue, ILogger<EmailWorkerHostedService> logger)
    {
        _queue = queue;
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        await foreach (var task in _queue.DequeueAllAsync(stoppingToken))
        {
            // Continue the trace from the enqueuing request. ContinueTrace returns a
            // TransactionContext that inherits trace_id + sampling decision from the headers.
            var transactionContext = SentrySdk.ContinueTrace(
                task.SentryTrace,
                task.Baggage,
                "queue.process_email",
                "queue.process");

            var transaction = SentrySdk.StartTransaction(transactionContext);
            SentrySdk.ConfigureScope(scope => scope.Transaction = transaction);

            transaction.SetData("queue.name", "email");
            transaction.SetData("queue.latency_ms",
                (DateTimeOffset.UtcNow - task.EnqueuedAt).TotalMilliseconds);

            try
            {
                await ProcessAsync(task, stoppingToken);
                transaction.Finish(SpanStatus.Ok);
                _logger.LogInformation("Email processed for {Email}", task.Email);
            }
            catch (Exception ex)
            {
                SentrySdk.CaptureException(ex);
                transaction.Finish(ex);
                _logger.LogError(ex, "Email worker failed for {Email}", task.Email);
            }
        }
    }

    private static async Task ProcessAsync(EmailTask task, CancellationToken ct)
    {
        var renderSpan = SentrySdk.GetSpan()?.StartChild("template.render", "email.render_welcome");
        await Task.Delay(120, ct);
        renderSpan?.Finish();

        var sendSpan = SentrySdk.GetSpan()?.StartChild("smtp.send", $"to {task.Email}");
        sendSpan?.SetData("smtp.server", "smtp.example.com");
        await Task.Delay(380, ct);

        // 10% simulated failure so customers see "failed background job" land as an issue.
        if (Random.Shared.NextDouble() < 0.10)
        {
            sendSpan?.Finish(SpanStatus.InternalError);
            throw new InvalidOperationException(
                $"SMTP relay rejected message for {task.Email}");
        }
        sendSpan?.Finish();
    }
}
