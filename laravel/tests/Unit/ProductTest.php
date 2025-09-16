<?php

namespace Tests\Unit;

use App\Models\Product;
use App\Models\Review;
use App\Models\Inventory;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class ProductTest extends TestCase
{
    use RefreshDatabase;

    /**
     * A basic unit test example.
     */
    public function test_example(): void
    {
        $this->assertTrue(true);
    }

    public function test_product_can_be_created_with_required_fields(): void
    {
        $product = Product::create([
            'title' => 'Test Wrench',
            'description' => 'A test wrench',
            'descriptionfull' => 'This is a detailed description of the test wrench',
            'price' => 1299,
            'img' => '/assets/test-wrench.jpg',
            'imgcropped' => '/assets/test-wrench-cropped.jpg',
        ]);

        $this->assertDatabaseHas('products', [
            'title' => 'Test Wrench',
            'price' => 1299,
        ]);
    }

    public function test_product_has_many_reviews(): void
    {
        $product = Product::factory()->create();
        $reviews = Review::factory(3)->create(['product_id' => $product->id]);

        $this->assertCount(3, $product->reviews);
        $this->assertInstanceOf(Review::class, $product->reviews->first());
    }

    public function test_product_has_many_inventory_items(): void
    {
        $product = Product::factory()->create();
        $inventory = Inventory::factory(2)->create(['product_id' => $product->id]);

        $this->assertCount(2, $product->inventory);
        $this->assertInstanceOf(Inventory::class, $product->inventory->first());
    }

    public function test_product_calculates_average_rating(): void
    {
        $product = Product::factory()->create();
        
        // Create reviews with ratings 4, 5, 3 (average = 4.0)
        Review::factory()->create(['product_id' => $product->id, 'rating' => 4]);
        Review::factory()->create(['product_id' => $product->id, 'rating' => 5]);
        Review::factory()->create(['product_id' => $product->id, 'rating' => 3]);

        $this->assertEquals(4.0, $product->average_rating);
    }

    public function test_product_returns_zero_average_rating_when_no_reviews(): void
    {
        $product = Product::factory()->create();
        
        $this->assertEquals(0.0, $product->average_rating);
    }

    public function test_product_counts_reviews(): void
    {
        $product = Product::factory()->create();
        Review::factory(5)->create(['product_id' => $product->id]);

        $this->assertEquals(5, $product->review_count);
    }

    public function test_product_formats_price_correctly(): void
    {
        $product = Product::factory()->create(['price' => 1299]); // $12.99

        $this->assertEquals('$12.99', $product->formatted_price);
    }

    public function test_product_formats_price_with_whole_dollars(): void
    {
        $product = Product::factory()->create(['price' => 2500]); // $25.00

        $this->assertEquals('$25.00', $product->formatted_price);
    }

    public function test_product_price_is_cast_to_integer(): void
    {
        $product = Product::factory()->create(['price' => '1299']);

        $this->assertIsInt($product->price);
        $this->assertEquals(1299, $product->price);
    }
}
