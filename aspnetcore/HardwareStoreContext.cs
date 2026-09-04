using System.Data.Common;
using Microsoft.EntityFrameworkCore.Diagnostics;

namespace Empower.Backend;

public class HardwareStoreContext : DbContext
{
    public HardwareStoreContext(DbContextOptions<HardwareStoreContext> options)
        : base(options)
    {
    }

    public virtual DbSet<Inventory> Inventory { get; set; } = null!;
    public virtual DbSet<Product> Products { get; set; } = null!;
    public virtual DbSet<PromoCode> PromoCodes { get; set; } = null!;
    public virtual DbSet<Review> Reviews { get; set; } = null!;
    public virtual DbSet<Tools> Tools { get; set; } = null!;

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Inventory>(entity =>
        {
            entity.ToTable("inventory");

            entity.Property(e => e.Id).HasColumnName("id");

            entity.Property(e => e.Count).HasColumnName("count");

            entity.Property(e => e.ProductId).HasColumnName("productid");

            entity.Property(e => e.Sku)
                .IsRequired()
                .HasColumnName("sku")
                .HasColumnType("character varying");
        });

        modelBuilder.Entity<Product>(entity =>
        {
            entity.ToTable("products");

            entity.HasIndex(e => e.Title)
                .HasDatabaseName("products_title_key")
                .IsUnique();

            entity.Property(e => e.Id).HasColumnName("id");

            entity.Property(e => e.Description)
                .IsRequired()
                .HasColumnName("description");

            entity.Property(e => e.DescriptionFull)
                .IsRequired()
                .HasColumnName("descriptionfull");

            entity.Property(e => e.Img)
                .IsRequired()
                .HasColumnName("img");

            entity.Property(e => e.ImgCropped)
                .IsRequired()
                .HasColumnName("imgcropped");

            entity.Property(e => e.Price).HasColumnName("price");

            entity.Property(e => e.Title)
                .IsRequired()
                .HasColumnName("title")
                .HasMaxLength(255);
        });

        modelBuilder.Entity<PromoCode>(entity =>
        {
            entity.ToTable("promo_codes");

            entity.Property(e => e.Id).HasColumnName("id");

            entity.Property(e => e.Code)
                .IsRequired()
                .HasColumnName("code")
                .HasMaxLength(50);

            entity.Property(e => e.PercentDiscount).HasColumnName("percent_discount");

            entity.Property(e => e.MaxDollarSavings).HasColumnName("max_dollar_savings");

            entity.Property(e => e.IsActive)
                .HasColumnName("is_active")
                .HasDefaultValue(true);

            entity.Property(e => e.ExpiresAt).HasColumnName("expires_at");

            entity.Property(e => e.CreatedAt)
                .HasColumnName("created_at")
                .HasDefaultValueSql("now()");
        });

        modelBuilder.Entity<Review>(entity =>
        {
            entity.ToTable("reviews");

            entity.Property(e => e.Id).HasColumnName("id");

            entity.Property(e => e.Created)
                .HasColumnName("created")
                .HasDefaultValueSql("now()");

            entity.Property(e => e.CustomerId).HasColumnName("customerid");

            entity.Property(e => e.Description).HasColumnName("description");

            entity.Property(e => e.ProductId).HasColumnName("productid");

            entity.Property(e => e.Rating).HasColumnName("rating");
        });

        modelBuilder.Entity<Tools>(entity =>
        {
            entity.ToTable("tools");

            entity.Property(e => e.Id).HasColumnName("id");

            entity.Property(e => e.Image)
                .IsRequired()
                .HasColumnName("image")
                .HasColumnType("character varying");

            entity.Property(e => e.Name)
                .IsRequired()
                .HasColumnName("name")
                .HasColumnType("character varying");

            entity.Property(e => e.Price).HasColumnName("price");

            entity.Property(e => e.Sku)
                .IsRequired()
                .HasColumnName("sku")
                .HasColumnType("character varying");

            entity.Property(e => e.Type)
                .IsRequired()
                .HasColumnName("type")
                .HasColumnType("character varying");
        });
    }
}

public class DemoCommandInterceptor : DbCommandInterceptor
{
    private readonly IHttpContextAccessor _httpContextAccessor;

    public DemoCommandInterceptor(IHttpContextAccessor httpContextAccessor)
    {
        _httpContextAccessor = httpContextAccessor;
    }

    public override async ValueTask<InterceptionResult<DbDataReader>> ReaderExecutingAsync(
        DbCommand command,
        CommandEventData eventData,
        InterceptionResult<DbDataReader> result,
        CancellationToken cancellationToken = default)
    {
        var delay = GetArtificialDelay();
        if (delay > TimeSpan.Zero)
        {
            await Task.Delay(delay, cancellationToken);
        }

        return await base.ReaderExecutingAsync(command, eventData, result, cancellationToken);
    }

    // Queries run at their real speed by default — a wall of uniform 1-3s spans is a dead
    // giveaway on a customer call. Opt into the slow-query demo per request with ?slow=true
    // (or ?slow=<milliseconds> for an exact delay), or globally with DB_SLOW_ALWAYS=true for
    // deployed-demo parity. This keeps the N+1 / slow-query / cache demos dramatic on demand
    // without making every trace look fake. The interceptor is a single instance, but
    // IHttpContextAccessor resolves the *current* request via AsyncLocal, so this is per-request.
    private TimeSpan GetArtificialDelay()
    {
        if (string.Equals(Environment.GetEnvironmentVariable("DB_SLOW_ALWAYS"), "true", StringComparison.OrdinalIgnoreCase))
        {
            return RandomDelay();
        }

        var query = _httpContextAccessor.HttpContext?.Request.Query;
        if (query is null || !query.TryGetValue("slow", out var slowValue))
        {
            return TimeSpan.Zero;
        }

        var raw = slowValue.ToString();

        // ?slow, ?slow=true, ?slow=1 -> random 1-3s
        if (string.IsNullOrEmpty(raw) || raw is "true" or "1")
        {
            return RandomDelay();
        }

        // ?slow=false, ?slow=0 -> no delay
        if (raw is "false" or "0")
        {
            return TimeSpan.Zero;
        }

        // ?slow=2500 -> exact milliseconds
        if (int.TryParse(raw, out var ms) && ms > 0)
        {
            return TimeSpan.FromMilliseconds(ms);
        }

        return TimeSpan.Zero;
    }

    // 1 to 3 seconds inclusive (Next upper bound is exclusive) — matches the original demo delay.
    private static TimeSpan RandomDelay() => TimeSpan.FromSeconds(Random.Shared.Next(1, 4));
}
