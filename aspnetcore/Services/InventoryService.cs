using Microsoft.EntityFrameworkCore;
using Empower.Backend.Models;

namespace Empower.Backend.Services;

public class InventoryService
{
    private readonly HardwareStoreContext _context;

    public InventoryService(HardwareStoreContext context)
    {
        _context = context;
    }

    public async Task<bool> ValidateAndUpdateInventoryAsync(Dictionary<string, int> items)
    {
        using var transaction = await _context.Database.BeginTransactionAsync();
        try
        {
            // Get all requested inventory items with a single query
            var skus = items.Keys.ToList();
            var inventoryItems = await _context.Inventory
                .Where(i => skus.Contains(i.Sku))
                .ToDictionaryAsync(i => i.Sku, i => i);

            // Validate all items have sufficient inventory
            foreach (var (sku, requestedQuantity) in items)
            {
                if (!inventoryItems.TryGetValue(sku, out var inventory))
                {
                    throw new InvalidOperationException($"Product with SKU {sku} not found");
                }

                if (inventory.Count < requestedQuantity)
                {
                    throw new InvalidOperationException($"Insufficient inventory for SKU {sku}. Available: {inventory.Count}, Requested: {requestedQuantity}");
                }
            }

            // Update inventory
            foreach (var (sku, requestedQuantity) in items)
            {
                var inventory = inventoryItems[sku];
                inventory.Count -= requestedQuantity;
            }

            await _context.SaveChangesAsync();
            await transaction.CommitAsync();
            return true;
        }
        catch (Exception)
        {
            await transaction.RollbackAsync();
            throw;
        }
    }
}