<?php

namespace Tests\Feature;

use App\Models\Product;
use App\Models\Inventory;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class CheckoutBugTest extends TestCase
{
    use RefreshDatabase;

    public function test_checkout_with_valid_cart_and_inventory_validation(): void
    {
        $product = Product::factory()->create([
            'title' => 'Test Product',
            'price' => 1000,
        ]);

        Inventory::factory()->create([
            'productid' => $product->id,
            'count' => 10,
            'sku' => 'TEST-SKU',
        ]);

        $response = $this->postJson('/api/checkout', [
            'cart' => [
                'quantities' => [
                    (string)$product->id => 2
                ],
                'items' => [
                    [
                        'id' => $product->id,
                        'title' => 'Test Product'
                    ]
                ]
            ],
            'form' => [
                'name' => 'Test User',
                'email' => 'test@example.com'
            ],
            'validate_inventory' => 'true'
        ]);

        $response->assertStatus(200)
                ->assertJson(['status' => 'success']);
    }

    public function test_checkout_empty_cart_throws_error(): void
    {
        $response = $this->postJson('/api/checkout', [
            'cart' => [
                'quantities' => [],
                'items' => []
            ],
            'form' => [
                'name' => 'Test User',
                'email' => 'test@example.com'
            ],
            'validate_inventory' => 'true'
        ]);

        $response->assertStatus(500);
    }
}
