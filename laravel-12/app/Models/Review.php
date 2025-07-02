<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Review extends Model
{
    use HasFactory;

    protected $fillable = [
        'product_id',
        'rating',
        'customer_id',
        'description',
    ];

    protected $casts = [
        'product_id' => 'integer',
        'rating' => 'integer',
        'customer_id' => 'integer',
    ];

    /**
     * Get the product that owns the review.
     */
    public function product(): BelongsTo
    {
        return $this->belongsTo(Product::class);
    }

    /**
     * Scope a query to only include reviews with a specific rating.
     */
    public function scopeWithRating($query, int $rating)
    {
        return $query->where('rating', $rating);
    }

    /**
     * Scope a query to only include recent reviews.
     */
    public function scopeRecent($query, int $days = 30)
    {
        return $query->where('created_at', '>=', now()->subDays($days));
    }
}
