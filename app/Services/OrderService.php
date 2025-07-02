<?php

namespace App\Services;

use App\Models\Product;
use App\Models\Inventory;
use Exception;

class OrderService
{
    /**
     * Check if an item is out of stock
     * Extracted from the original isOutOfStock() function
     */
    public function isOutOfStock(Product $product): bool
    {
        $inventory = $product->inventory()->first();
        
        if (!$inventory) {
            return true; // No inventory record = out of stock
        }
        
        return $inventory->count <= 0;
    }

    /**
     * Process an order with inventory checking
     * Extracted from the original process_order() function
     */
    public function processOrder(array $cart): void
    {
        foreach ($cart as $product) {
            if ($this->isOutOfStock($product)) {
                throw new Exception("Not enough inventory for {$product->id}");
            } else {
                $this->decrementInventory($product);
            }
        }
    }

    /**
     * Get all inventory
     * Extracted from the original get_inventory() function
     */
    public function getInventory()
    {
        return Inventory::all();
    }

    /**
     * Decrement inventory for a product
     * Extracted from the original decrementInventory() function
     * Note: Original used Cache, we're using database for simplicity
     */
    private function decrementInventory(Product $product): void
    {
        $inventory = $product->inventory()->first();
        
        if ($inventory && $inventory->count > 0) {
            $inventory->decrementStock(1);
        }
    }
} 