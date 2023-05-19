namespace Empower.Backend.Models;

public class Inventory
{
    public required int Id { get; set; }
    public required string Sku { get; set; }
    public required int Count { get; set; }
    public int? ProductId { get; set; }
}
