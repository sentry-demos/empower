<?php

namespace Tests\Unit;

use App\Models\Inventory;
use App\Models\Product;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class InventoryTest extends TestCase
{
    use RefreshDatabase;

    /**
     * A basic unit test example.
     */
    public function test_example(): void
    {
        $this->assertTrue(true);
    }

    public function test_inventory_can_be_created_with_required_fields(): void
    {
        $product = Product::factory()->create();
        
        $inventory = Inventory::create([
            'sku' => 'TEST123',
            'count' => 50,
            'product_id' => $product->id,
        ]);

        $this->assertDatabaseHas('inventories', [
            'sku' => 'TEST123',
            'count' => 50,
            'product_id' => $product->id,
        ]);
    }

    public function test_inventory_belongs_to_product(): void
    {
        $product = Product::factory()->create();
        $inventory = Inventory::factory()->create(['product_id' => $product->id]);

        $this->assertInstanceOf(Product::class, $inventory->product);
        $this->assertEquals($product->id, $inventory->product->id);
    }

    public function test_inventory_is_in_stock_when_count_greater_than_zero(): void
    {
        $inventory = Inventory::factory()->create(['count' => 5]);

        $this->assertTrue($inventory->isInStock());
        $this->assertFalse($inventory->isOutOfStock());
    }

    public function test_inventory_is_out_of_stock_when_count_is_zero(): void
    {
        $inventory = Inventory::factory()->create(['count' => 0]);

        $this->assertFalse($inventory->isInStock());
        $this->assertTrue($inventory->isOutOfStock());
    }

    public function test_inventory_is_out_of_stock_when_count_is_negative(): void
    {
        $inventory = Inventory::factory()->create(['count' => -1]);

        $this->assertFalse($inventory->isInStock());
        $this->assertTrue($inventory->isOutOfStock());
    }

    public function test_inventory_can_decrement_stock_when_sufficient(): void
    {
        $inventory = Inventory::factory()->create(['count' => 10]);

        $result = $inventory->decrementStock(3);

        $this->assertTrue($result);
        $this->assertEquals(7, $inventory->fresh()->count);
    }

    public function test_inventory_cannot_decrement_stock_when_insufficient(): void
    {
        $inventory = Inventory::factory()->create(['count' => 5]);

        $result = $inventory->decrementStock(10);

        $this->assertFalse($result);
        $this->assertEquals(5, $inventory->fresh()->count); // Should remain unchanged
    }

    public function test_inventory_decrement_stock_defaults_to_one(): void
    {
        $inventory = Inventory::factory()->create(['count' => 10]);

        $result = $inventory->decrementStock();

        $this->assertTrue($result);
        $this->assertEquals(9, $inventory->fresh()->count);
    }

    public function test_inventory_can_increment_stock(): void
    {
        $inventory = Inventory::factory()->create(['count' => 5]);

        $inventory->incrementStock(3);

        $this->assertEquals(8, $inventory->fresh()->count);
    }

    public function test_inventory_increment_stock_defaults_to_one(): void
    {
        $inventory = Inventory::factory()->create(['count' => 5]);

        $inventory->incrementStock();

        $this->assertEquals(6, $inventory->fresh()->count);
    }

    public function test_inventory_scope_in_stock_filters_correctly(): void
    {
        Inventory::factory()->create(['count' => 10]); // In stock
        Inventory::factory()->create(['count' => 5]);  // In stock
        Inventory::factory()->create(['count' => 0]);  // Out of stock
        Inventory::factory()->create(['count' => -1]); // Out of stock

        $inStockCount = Inventory::inStock()->count();

        $this->assertEquals(2, $inStockCount);
    }

    public function test_inventory_scope_out_of_stock_filters_correctly(): void
    {
        Inventory::factory()->create(['count' => 10]); // In stock
        Inventory::factory()->create(['count' => 5]);  // In stock
        Inventory::factory()->create(['count' => 0]);  // Out of stock
        Inventory::factory()->create(['count' => -1]); // Out of stock

        $outOfStockCount = Inventory::outOfStock()->count();

        $this->assertEquals(2, $outOfStockCount);
    }

    public function test_inventory_sku_must_be_unique(): void
    {
        Inventory::factory()->create(['sku' => 'UNIQUE123']);

        $this->expectException(\Illuminate\Database\QueryException::class);
        
        Inventory::factory()->create(['sku' => 'UNIQUE123']);
    }

    public function test_inventory_count_is_cast_to_integer(): void
    {
        $inventory = Inventory::factory()->create(['count' => '25']);

        $this->assertIsInt($inventory->count);
        $this->assertEquals(25, $inventory->count);
    }
}
