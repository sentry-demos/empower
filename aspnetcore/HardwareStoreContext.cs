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
