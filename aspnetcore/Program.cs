// Create the web application builder.
var builder = WebApplication.CreateBuilder(args);

// Configure API controllers, and JSON serialization options.
builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        // Prevent cycles due to EF Core navigation properties.
        options.JsonSerializerOptions.ReferenceHandler = ReferenceHandler.IgnoreCycles;
        
        // Don't serialize properties that are null.
        options.JsonSerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
    });

// Setup CORS to allow anything.
builder.Services.AddCors(options => options.AddDefaultPolicy(policy => policy
    .AllowAnyOrigin()
    .AllowAnyHeader()
    .AllowAnyMethod()));

// Add the database context.
builder.Services.AddDbContext<HardwareStoreContext>(options =>
{
    var connectionString = AppUtils.GetConnectionString(builder.Configuration);
    options.UseNpgsql(connectionString);
});

// Initialize Sentry.
builder.WebHost.UseSentry(options =>
{
    // Use the environment variables set by the startup scripts.
    options.Dsn = Environment.GetEnvironmentVariable("ASPNETCORE_APP_DSN");
    options.Release = Environment.GetEnvironmentVariable("RELEASE");
    
    // Enable some features.
    options.TracesSampleRate = 1.0;
    options.AutoSessionTracking = true;
    options.SendDefaultPii = true;

    // In development, allow the Sentry SDK to emit debug info to the console.
    if (builder.Environment.IsDevelopment())
    {
        options.Debug = true;
    }
});

// Build the application.
var app = builder.Build();

// Add middleware components, including Sentry Tracing.
app.UseCors();
app.UseSentryTracing();
app.MapControllers();

// Run the application.
app.Run();
