namespace Empower.Backend.Controllers;

[ApiController]
[Route("blocking")]
public class BlockingController : ControllerBase
{
    [HttpGet]
    public string Get()
    {
        // DEMO: deliberate sync-over-async. Blocking the request thread while waiting on
        // an async call is a classic ThreadPool-starvation anti-pattern. With
        // CaptureBlockingCalls=true the SDK flags it, and because the block happens HERE
        // (in our code, marked in-app via AddInAppInclude) the Sentry stack trace points
        // straight at this line — unlike a framework-internal blocking call, which isn't
        // actionable. The fix a customer would make: 'await' instead of '.Wait()'.
        Task.Delay(500).Wait();

        return "aspnetcore /blocking — deliberately blocked the request thread (fix: use await)";
    }
}
