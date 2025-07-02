<?php

namespace Tests\Unit;

use App\Models\Product;
use App\Models\Inventory;
use App\Services\OrderService;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class OrderServiceTest extends TestCase
{
    use RefreshDatabase;

    protected OrderService $orderService;

    protected function setUp(): void
    {
        parent::setUp();
        $this->orderService = new OrderService();
    }

    public function test_can_check_if_item_is_out_of_stock(): void
    {
        $product = Product::factory()->create();
        $inventory = Inventory::factory()->create([
            'product_id' => $product->id,
            'count' => 0
        ]);

        $result = $this->orderService->isOutOfStock($product);

        $this->assertTrue($result);
    }

    public function test_can_check_if_item_is_in_stock(): void
    {
        $product = Product::factory()->create();
        $inventory = Inventory::factory()->create([
            'product_id' => $product->id,
            'count' => 5
        ]);

        $result = $this->orderService->isOutOfStock($product);

        $this->assertFalse($result);
    }

    public function test_can_process_order_when_items_in_stock(): void
    {
        $product1 = Product::factory()->create();
        $product2 = Product::factory()->create();
        
        Inventory::factory()->create(['product_id' => $product1->id, 'count' => 10]);
        Inventory::factory()->create(['product_id' => $product2->id, 'count' => 5]);

        $cart = [$product1, $product2];

        // Should not throw exception
        $this->orderService->processOrder($cart);
        
        // Should decrement inventory
        $this->assertEquals(9, $product1->inventory()->first()->count);
        $this->assertEquals(4, $product2->inventory()->first()->count);
    }

    public function test_throws_exception_when_processing_order_with_out_of_stock_item(): void
    {
        $product = Product::factory()->create();
        Inventory::factory()->create(['product_id' => $product->id, 'count' => 0]);

        $cart = [$product];

        $this->expectException(\Exception::class);
        $this->expectExceptionMessage("Not enough inventory for {$product->id}");

        $this->orderService->processOrder($cart);
    }

    public function test_can_get_inventory_for_all_products(): void
    {
        $product1 = Product::factory()->create();
        $product2 = Product::factory()->create();
        
        Inventory::factory()->create(['product_id' => $product1->id, 'count' => 10]);
        Inventory::factory()->create(['product_id' => $product2->id, 'count' => 5]);

        $inventory = $this->orderService->getInventory();

        $this->assertCount(2, $inventory);
    }
}
