using System;
using Microsoft.Extensions.Configuration;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata;

// Code scaffolded by EF Core assumes nullable reference types (NRTs) are not used or disabled.
// If you have enabled NRTs for your project, then un-comment the following line:
// #nullable disable

namespace aspnetcore.Models
{
    public partial class hardwarestoreContext : DbContext
    {
        public hardwarestoreContext(IConfiguration configuration)
        {
            Configuration = configuration;
        }

        public hardwarestoreContext(IConfiguration configuration, DbContextOptions<hardwarestoreContext> options)
            : base(options)
        {
            Configuration = configuration;
        }
        
        public IConfiguration Configuration { get; }

        public virtual DbSet<Inventory> Inventory { get; set; }
        public virtual DbSet<Product> Products { get; set; }
        public virtual DbSet<Review> Reviews { get; set; }
        public virtual DbSet<Tools> Tools { get; set; }

        protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        {
            if (!optionsBuilder.IsConfigured)
            {
                optionsBuilder.UseNpgsql(Configuration.GetConnectionString("DefaultConnection"));
            }
        }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            modelBuilder.Entity<Inventory>(entity =>
            {
                entity.ToTable("inventory");

                entity.Property(e => e.Id).HasColumnName("id");

                entity.Property(e => e.Count).HasColumnName("count");

                entity.Property(e => e.Productid).HasColumnName("productid");

                entity.Property(e => e.Sku)
                    .IsRequired()
                    .HasColumnName("sku")
                    .HasColumnType("character varying");
            });

            modelBuilder.Entity<Product>(entity =>
            {
                entity.ToTable("products");

                entity.HasIndex(e => e.Title)
                    .HasName("products_title_key")
                    .IsUnique();

                entity.Property(e => e.Id).HasColumnName("id");

                entity.Property(e => e.Description)
                    .IsRequired()
                    .HasColumnName("description");

                entity.Property(e => e.Descriptionfull)
                    .IsRequired()
                    .HasColumnName("descriptionfull");

                entity.Property(e => e.Img)
                    .IsRequired()
                    .HasColumnName("img");

                entity.Property(e => e.Imgcropped)
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

                entity.Property(e => e.Customerid).HasColumnName("customerid");

                entity.Property(e => e.Description).HasColumnName("description");

                entity.Property(e => e.Productid).HasColumnName("productid");

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

            OnModelCreatingPartial(modelBuilder);
        }

        partial void OnModelCreatingPartial(ModelBuilder modelBuilder);
    }
}
