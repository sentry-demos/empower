namespace Empower.Backend.Models;

public class Review
{
    public required int Id { get; set; }
    public required int ProductId { get; set; }
    public required int Rating { get; set; }
    public int? CustomerId { get; set; }
    public string? Description { get; set; }
    public DateTime? Created { get; set; }
    public required Product Product { get; set; }
}
