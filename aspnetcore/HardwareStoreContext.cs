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
    public virtual DbSet<Review> Reviews { get; set; } = null!;
    public virtual DbSet<Tools> Tools { get; set; } = null!;
    public virtual DbSet<Order> Orders { get; set; } = null!;

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

        modelBuilder.Entity<Order>(entity =>
        {
            entity.ToTable("orders");

            entity.Property(e => e.Id).HasColumnName("id");

            entity.Property(e => e.OrderDate).HasColumnName("order_date");

            entity.Property(e => e.Total).HasColumnName("total");
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
    public override async ValueTask<InterceptionResult<DbDataReader>> ReaderExecutingAsync(
        DbCommand command,
        CommandEventData eventData,
        InterceptionResult<DbDataReader> result,
        CancellationToken cancellationToken = default)
    {
        // for demoing slowness of db query
        await Task.Delay(TimeSpan.FromSeconds(Random.Shared.Next(1, 3)), cancellationToken);
        
        return await base.ReaderExecutingAsync(command, eventData, result, cancellationToken);
    }
}
