namespace Empower.Backend.Models;

public class Product
{
    public required int Id { get; set; }
    public required string Title { get; set; }
    public required string Description { get; set; }
    public required string DescriptionFull { get; set; }
    public required int Price { get; set; }
    public required string Img { get; set; }
    public required string ImgCropped { get; set; }
    public required ICollection<Review> Reviews { get; set; }
}
