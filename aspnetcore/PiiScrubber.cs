using System.Text.RegularExpressions;

namespace Empower.Backend;

// Scrubs sensitive headers, card-shape numbers, and secret-bearing JSON values
// before events leave the SDK. Project-level Data Scrubbing rules are the
// second line of defense.
//
// user.email is intentionally NOT scrubbed — it's set by AppMiddleware to
// identify SE/customer demo scenarios.
public static class PiiScrubber
{
    private const string FilteredHeaderValue = "[Filtered]";
    private const string CardRedactedValue = "[CARD_REDACTED]";
    private const string GenericRedactedValue = "[REDACTED]";

    private static readonly HashSet<string> SensitiveHeaders =
        new(StringComparer.OrdinalIgnoreCase)
        {
            "Authorization",
            "Cookie",
            "Set-Cookie",
            "X-API-Key",
            "X-Api-Key",
        };

    private static readonly Regex CardPattern = new(
        @"\b(?:\d[ -]*?){13,19}\b",
        RegexOptions.Compiled);

    private static readonly Regex SecretKeyPattern = new(
        @"""(password|ssn|secret|api_key|apikey|token)""\s*:\s*""[^""]*""",
        RegexOptions.IgnoreCase | RegexOptions.Compiled);

    public static void Scrub(SentryEvent sentryEvent)
    {
        ScrubRequest(sentryEvent.Request);

        if (sentryEvent.SentryExceptions is not null)
        {
            foreach (var ex in sentryEvent.SentryExceptions)
            {
                if (!string.IsNullOrEmpty(ex.Value))
                {
                    ex.Value = ScrubString(ex.Value);
                }
            }
        }

        if (sentryEvent.Message is { } msg)
        {
            if (msg.Message is not null) msg.Message = ScrubString(msg.Message);
            if (msg.Formatted is not null) msg.Formatted = ScrubString(msg.Formatted);
        }
    }

    public static Breadcrumb? Scrub(Breadcrumb breadcrumb)
    {
        if (string.IsNullOrEmpty(breadcrumb.Message)) return breadcrumb;

        var scrubbed = ScrubString(breadcrumb.Message);
        if (ReferenceEquals(scrubbed, breadcrumb.Message)) return breadcrumb;

        // Breadcrumb is immutable; rebuild with scrubbed message. Loses original timestamp.
        return new Breadcrumb(
            message: scrubbed,
            type: breadcrumb.Type ?? string.Empty,
            data: breadcrumb.Data,
            category: breadcrumb.Category,
            level: breadcrumb.Level);
    }

    // Shared by event + transaction paths since both carry SentryRequest with body.
    public static void ScrubRequest(SentryRequest? request)
    {
        if (request is null) return;

        ScrubHeaders(request.Headers);

        if (request.Data is string bodyString)
        {
            request.Data = ScrubString(bodyString);
        }
    }

    private static void ScrubHeaders(IDictionary<string, string>? headers)
    {
        if (headers is null) return;

        foreach (var key in headers.Keys.ToList())
        {
            if (SensitiveHeaders.Contains(key))
            {
                headers[key] = FilteredHeaderValue;
            }
        }
    }

    private static string ScrubString(string input)
    {
        var scrubbed = SecretKeyPattern.Replace(input, match =>
        {
            var colonIndex = match.Value.IndexOf(':');
            return match.Value.Substring(0, colonIndex + 1) + $"\"{GenericRedactedValue}\"";
        });

        scrubbed = CardPattern.Replace(scrubbed, match =>
        {
            // Filter by digit count — regex over-matches on long digit sequences (e.g. trace IDs).
            var digitCount = match.Value.Count(char.IsDigit);
            return digitCount >= 13 && digitCount <= 19 ? CardRedactedValue : match.Value;
        });

        return scrubbed;
    }
}
