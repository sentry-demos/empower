using System.Threading.Channels;

namespace Empower.Backend;

// Captured from the HTTP request scope at enqueue time so the worker can continue
// the same Sentry trace when it later processes the task.
public record EmailTask(
    string Email,
    string? SentryTrace,
    string? Baggage,
    DateTimeOffset EnqueuedAt);

public interface IEmailQueue
{
    ValueTask EnqueueAsync(EmailTask task, CancellationToken cancellationToken = default);
    IAsyncEnumerable<EmailTask> DequeueAllAsync(CancellationToken cancellationToken);
}

// Single-process Channel-backed queue. Real .NET apps would point this at Hangfire,
// MassTransit, Azure Service Bus, etc. — the Sentry instrumentation pattern is the
// same regardless of transport: capture sentry-trace + baggage at enqueue, continue
// the trace at dequeue.
public class ChannelEmailQueue : IEmailQueue
{
    private readonly Channel<EmailTask> _channel = Channel.CreateUnbounded<EmailTask>(
        new UnboundedChannelOptions { SingleReader = true, SingleWriter = false });

    public ValueTask EnqueueAsync(EmailTask task, CancellationToken cancellationToken = default) =>
        _channel.Writer.WriteAsync(task, cancellationToken);

    public IAsyncEnumerable<EmailTask> DequeueAllAsync(CancellationToken cancellationToken) =>
        _channel.Reader.ReadAllAsync(cancellationToken);
}
