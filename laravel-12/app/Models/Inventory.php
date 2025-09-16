<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Inventory extends Model
{
    use HasFactory;

    protected $fillable = [
        'sku',
        'count',
        'product_id',
    ];

    protected $casts = [
        'count' => 'integer',
        'product_id' => 'integer',
    ];

    /**
     * Get the product that owns the inventory.
     */
    public function product(): BelongsTo
    {
        return $this->belongsTo(Product::class);
    }

    /**
     * Check if the item is in stock.
     */
    public function isInStock(): bool
    {
        return $this->count > 0;
    }

    /**
     * Check if the item is out of stock.
     */
    public function isOutOfStock(): bool
    {
        return $this->count <= 0;
    }

    /**
     * Decrement the inventory count.
     */
    public function decrementStock(int $quantity = 1): bool
    {
        if ($this->count >= $quantity) {
            $this->decrement('count', $quantity);
            return true;
        }
        return false;
    }

    /**
     * Increment the inventory count.
     */
    public function incrementStock(int $quantity = 1): void
    {
        $this->increment('count', $quantity);
    }

    /**
     * Scope a query to only include items in stock.
     */
    public function scopeInStock($query)
    {
        return $query->where('count', '>', 0);
    }

    /**
     * Scope a query to only include items out of stock.
     */
    public function scopeOutOfStock($query)
    {
        return $query->where('count', '<=', 0);
    }
}
