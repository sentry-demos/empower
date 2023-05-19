namespace Empower.Backend.Models;

public class Tools
{
    public required int Id { get; set; }
    public required string Name { get; set; }
    public required string Type { get; set; }
    public required string Sku { get; set; }
    public required string Image { get; set; }
    public required int Price { get; set; }
}
