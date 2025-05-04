<?php

namespace Tests\Unit;

use Tests\TestCase;
use App\Product;
use App\Inventory;
use Illuminate\Foundation\Testing\RefreshDatabase;

class InventoryTest extends TestCase
{
    use RefreshDatabase;
    
    protected function setUp(): void
    {
        parent::setUp();
        
        // Create test products
        Product::create([
            'id' => 1,
            'name' => 'Test Wrench',
            'price' => 10.00
        ]);
    }

    /**
     * Test checkout with insufficient inventory
     */
    public function testCheckoutWithInsufficientInventory()
    {
        // Create cart with quantity more than available inventory
        $cart = [
            (object)[
                'id' => 1,
                'quantity' => 2 // More than available inventory (1)
            ]
        ];

        // Set initial inventory
        Inventory::create([
            'product_id' => 1,
            'quantity' => 1
        ]);

        // Make POST request to checkout endpoint
        $response = $this->postJson('/checkout', [
            'cart' => $cart,
            'validate_inventory' => 'true',
            'form' => [
                'email' => 'test@example.com',
                'firstName' => 'Test',
                'lastName' => 'User'
            ]
        ]);

        // Assert response status is 400 (Bad Request)
        $response->assertStatus(400);
        
        // Assert error message
        $response->assertJson([
            'error' => 'Insufficient inventory for product: Test Wrench'
        ]);
    }

    /**
     * Test checkout with sufficient inventory
     */
    public function testCheckoutWithSufficientInventory()
    {
        // Create cart with quantity less than or equal to available inventory
        $cart = [
            (object)[
                'id' => 1,
                'quantity' => 1
            ]
        ];

        // Set initial inventory
        Inventory::create([
            'product_id' => 1,
            'quantity' => 1
        ]);

        // Make POST request to checkout endpoint
        $response = $this->postJson('/checkout', [
            'cart' => $cart,
            'validate_inventory' => 'true',
            'form' => [
                'email' => 'test@example.com',
                'firstName' => 'Test',
                'lastName' => 'User'
            ]
        ]);

        // Assert response is successful
        $response->assertStatus(200);

        // Assert inventory was decremented
        $this->assertEquals(0, Inventory::where('product_id', 1)->first()->quantity);
    }
}