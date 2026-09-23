namespace Empower.Backend.Models;

public class PromoCode
{
    public int Id { get; set; }
    public required string Code { get; set; }
    public int? PercentDiscount { get; set; }
    public int? MaxDollarSavings { get; set; }
    public bool? IsActive { get; set; }
    public DateTime? ExpiresAt { get; set; }
    public DateTime? CreatedAt { get; set; }
}
