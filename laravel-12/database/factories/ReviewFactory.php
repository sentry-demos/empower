<?php

namespace Database\Factories;

use App\Models\Product;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends \Illuminate\Database\Eloquent\Factories\Factory<\App\Models\Review>
 */
class ReviewFactory extends Factory
{
    /**
     * Define the model's default state.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        $reviews = [
            'Excellent quality tool! Works perfectly.',
            'Great value for the money. Highly recommended.',
            'Solid construction and very durable.',
            'Does exactly what I needed it for.',
            'Good product, fast shipping.',
            'Perfect for my DIY projects.',
            'Better than expected quality.',
            'Would definitely buy again.',
            'Great addition to my toolbox.',
            'Professional grade tool at a great price.'
        ];

        return [
            'product_id' => Product::factory(),
            'rating' => $this->faker->numberBetween(3, 5), // Mostly positive reviews
            'customer_id' => $this->faker->numberBetween(1, 1000),
            'description' => $this->faker->randomElement($reviews),
        ];
    }
}
