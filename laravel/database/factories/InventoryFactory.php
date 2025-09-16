<?php

namespace Database\Factories;

use App\Models\Product;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends \Illuminate\Database\Eloquent\Factories\Factory<\App\Models\Inventory>
 */
class InventoryFactory extends Factory
{
    /**
     * Define the model's default state.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        return [
            'sku' => $this->faker->unique()->regexify('[A-Z]{3}[0-9]{3}'),
            'count' => $this->faker->numberBetween(0, 100),
            'product_id' => Product::factory(),
        ];
    }

    /**
     * Indicate that the inventory is out of stock.
     */
    public function outOfStock(): static
    {
        return $this->state(fn (array $attributes) => [
            'count' => 0,
        ]);
    }

    /**
     * Indicate that the inventory is well stocked.
     */
    public function wellStocked(): static
    {
        return $this->state(fn (array $attributes) => [
            'count' => $this->faker->numberBetween(50, 100),
        ]);
    }
}
