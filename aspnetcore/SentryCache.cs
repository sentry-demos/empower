using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.Extensions.Caching.Memory;

namespace Empower.Backend;

// Thin IMemoryCache wrapper that emits Sentry "cache.get" / "cache.put" spans
// following Sentry's Caches-module span convention. The .NET SDK does NOT
// auto-instrument caches (the Python SDK does), so we emit these by hand — and
// THAT is what makes backend-aspnetcore show up in Sentry > Insights > Caches
// next to flask. The module is derived purely from this span op + attribute
// contract, not from any SDK magic:
//
//   op = "cache.get"   data: cache.hit (bool), cache.key (string[]),
//                            cache.item_size (bytes, on hit)
//   op = "cache.put"   data: cache.key (string[]), cache.item_size (bytes)
//
// The span description is the cache key (matches flask's "<key>" descriptions).
public class SentryCache
{
    private readonly IMemoryCache _cache;

    // Cached entities have EF back-references (Review.Product) — ignore cycles
    // so the size estimate never throws on the demo's product graph.
    private static readonly JsonSerializerOptions SizeOpts = new()
    {
        ReferenceHandler = ReferenceHandler.IgnoreCycles,
    };

    public SentryCache(IMemoryCache cache) => _cache = cache;

    public bool TryGet<T>(string key, out T? value)
    {
        var span = SentrySdk.GetSpan()?.StartChild("cache.get", key);
        var hit = _cache.TryGetValue(key, out var cached);

        span?.SetData("cache.hit", hit);
        span?.SetData("cache.key", new[] { key });

        if (hit && cached is T typed)
        {
            span?.SetData("cache.item_size", EstimateSize(typed));
            value = typed;
        }
        else
        {
            hit = false;
            value = default;
        }

        span?.Finish();
        return hit;
    }

    public void Set<T>(string key, T value, TimeSpan ttl)
    {
        var span = SentrySdk.GetSpan()?.StartChild("cache.put", key);

        _cache.Set(key, value, ttl);

        span?.SetData("cache.key", new[] { key });
        span?.SetData("cache.item_size", EstimateSize(value));
        span?.Finish();
    }

    // Approximate byte size via UTF-8 JSON — good enough for the Caches module's
    // "average item size" panel; not meant to be exact.
    private static long EstimateSize<T>(T value)
    {
        try { return JsonSerializer.SerializeToUtf8Bytes(value, SizeOpts).LongLength; }
        catch { return 0; }
    }
}
