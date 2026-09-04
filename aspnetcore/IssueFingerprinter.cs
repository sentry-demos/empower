using System.Text.RegularExpressions;

namespace Empower.Backend;

// Custom fingerprint that collapses noise: only prod-tda SE values split per
// env+release (Release Health needs that granularity); local/QA/ad-hoc SE
// testing all groups by exception type + backend so dashboards stay quiet.
// See https://docs.sentry.io/platforms/dotnet/usage/sdk-fingerprinting/
public static class IssueFingerprinter
{
    private const string DefaultPlaceholder = "{{ default }}";
    private const string BackendTypePlaceholder = "{{ tags.backendType }}";
    private const string UndefinedSentinel = "undefined";

    // Collapse "prod-tda-firefox-checkout-test1" → "prod-tda-". Browser axis
    // dropped: backend exceptions don't vary per browser.
    private static readonly Regex SeTdaPrefixPattern = new(@"^[^-]+-tda-", RegexOptions.Compiled);

    public static void Fingerprint(SentryEvent sentryEvent)
    {
        // Performance issues are detected server-side and don't pass through this hook.
        var isErrorEvent = sentryEvent.SentryExceptions?.Any() == true;
        if (!isErrorEvent) return;

        var fingerprint = new List<string> { DefaultPlaceholder };

        // Only prod-tda gets per-SE splitting (for Release Health). Everything
        // else — no SE, undefined SE, qa-tda, ad-hoc SE — collapses by
        // exception type + backend so we don't create N issues for one bug.
        var se = sentryEvent.Tags.TryGetValue("se", out var seValue) ? seValue : null;
        if (!string.IsNullOrEmpty(se) && se != UndefinedSentinel && se.StartsWith("prod-tda-"))
        {
            fingerprint.Add(ExtractSeFingerprint(se));
            if (!string.IsNullOrEmpty(sentryEvent.Release))
            {
                fingerprint.Add(sentryEvent.Release);
            }
        }

        fingerprint.Add(BackendTypePlaceholder);
        sentryEvent.SetFingerprint(fingerprint);
    }

    private static string ExtractSeFingerprint(string se)
    {
        var match = SeTdaPrefixPattern.Match(se);
        return match.Success ? match.Value : se;
    }
}
