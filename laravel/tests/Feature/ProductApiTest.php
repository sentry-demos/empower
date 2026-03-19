<?php

namespace Tests\Feature;

use App\Models\Product;
use App\Models\Review;
use App\Models\Inventory;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class ProductApiTest extends TestCase
{
    use RefreshDatabase;

    public function test_can_get_products_with_reviews(): void
    {
        // Create products like the original app
        $product = Product::factory()->create([
            'title' => 'Plant Mood',
            'description' => 'The mood ring for plants.',
            'price' => 1550, // $15.50
        ]);

        // Create some reviews
        Review::factory()->create(['productid' => $product->id, 'rating' => 5]);
        Review::factory()->create(['productid' => $product->id, 'rating' => 4]);

        $response = $this->getJson('/api/products');

        $response->assertStatus(200)
                ->assertJsonCount(1)
                ->assertJsonPath('0.title', 'Plant Mood')
                ->assertJsonPath('0.price', 1550)
                ->assertJsonStructure([
                    '*' => [
                        'id',
                        'title',
                        'description',
                        'price',
                        'reviews' => [
                            '*' => [
                                'id',
                                'rating',
                                'description'
                            ]
                        ]
                    ]
                ]);
    }

    public function test_checkout_throws_exception_for_insufficient_inventory(): void
    {
        $product = Product::factory()->create();
        Inventory::factory()->create(['productid' => $product->id, 'count' => 0]);

        $response = $this->postJson('/api/checkout', [
            'items' => [$product->id]
        ]);

        $response->assertStatus(500); // Exception should be thrown
    }

    public function test_can_get_inventory_levels(): void
    {
        $product1 = Product::factory()->create();
        $product2 = Product::factory()->create();

        Inventory::factory()->create(['productid' => $product1->id, 'count' => 10, 'sku' => 'SKU001']);
        Inventory::factory()->create(['productid' => $product2->id, 'count' => 5, 'sku' => 'SKU002']);

        $response = $this->getJson('/api/inventory');

        $response->assertStatus(200)
                ->assertJsonCount(2)
                ->assertJsonStructure([
                    '*' => [
                        'id',
                        'sku',
                        'count',
                        'product_id'
                    ]
                ]);
    }

    public function test_handled_exception_endpoint(): void
    {
        $response = $this->getJson('/api/handled');

        $response->assertStatus(200);
        // Should return exception details but not crash
    }

    public function test_unhandled_exception_endpoint(): void
    {
        $response = $this->getJson('/api/unhandled');

        $response->assertStatus(500);
        // Should trigger an actual error (division by zero)
    }

    public function test_products_endpoint_returns_empty_when_no_products(): void
    {
        $response = $this->getJson('/api/products');

        $response->assertStatus(200)
                ->assertJson([]);
    }

    public function test_products_with_no_reviews(): void
    {
        $product = Product::factory()->create();

        $response = $this->getJson('/api/products');

        $response->assertStatus(200)
                ->assertJsonCount(1)
                ->assertJsonPath('0.reviews', []);
    }

    public function test_products_join_returns_products_with_reviews(): void
    {
        // Create products
        $product1 = Product::factory()->create([
            'title' => 'Plant Mood',
            'description' => 'The mood ring for plants.',
            'price' => 155,
        ]);

        $product2 = Product::factory()->create([
            'title' => 'Plant-to-Text',
            'description' => 'Turn plant thoughts into text.',
            'price' => 89,
        ]);

        // Create reviews for product1
        Review::factory()->create([
            'productid' => $product1->id,
            'rating' => 5,
            'description' => 'Amazing product!'
        ]);
        Review::factory()->create([
            'productid' => $product1->id,
            'rating' => 4,
            'description' => 'Very good'
        ]);

        // Create review for product2
        Review::factory()->create([
            'productid' => $product2->id,
            'rating' => 5,
            'description' => 'Love it!'
        ]);

        $response = $this->getJson('/products-join');

        $response->assertStatus(200)
                ->assertJsonCount(2)
                ->assertJsonStructure([
                    '*' => [
                        'id',
                        'title',
                        'description',
                        'price',
                        'reviews' => [
                            '*' => [
                                'id',
                                'productid',
                                'rating',
                                'customerId',
                                'description',
                                'created',
                            ]
                        ]
                    ]
                ]);

        // Verify product1 has 2 reviews
        $data = $response->json();
        $product1Data = collect($data)->firstWhere('id', $product1->id);
        $this->assertCount(2, $product1Data['reviews']);

        // Verify product2 has 1 review
        $product2Data = collect($data)->firstWhere('id', $product2->id);
        $this->assertCount(1, $product2Data['reviews']);
    }

    public function test_products_join_handles_products_without_reviews(): void
    {
        $product = Product::factory()->create([
            'title' => 'Test Product',
            'price' => 100,
        ]);

        $response = $this->getJson('/products-join');

        $response->assertStatus(200)
                ->assertJsonCount(1);

        $data = $response->json();
        $this->assertEmpty($data[0]['reviews'], 'Product should have empty reviews array');
    }

    public function test_products_join_returns_empty_array_when_no_products(): void
    {
        $response = $this->getJson('/products-join');

        $response->assertStatus(200)
                ->assertJson([]);
    }
}
