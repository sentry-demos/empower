<?php

namespace Database\Factories;

use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends \Illuminate\Database\Eloquent\Factories\Factory<\App\Models\Product>
 */
class ProductFactory extends Factory
{
    /**
     * Define the model's default state.
     *
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        $products = [
            [
                'title' => 'Wrench',
                'description' => 'A essential tool for any toolbox',
                'descriptionfull' => 'This high-quality wrench is made from durable steel and features a comfortable grip handle. Perfect for all your mechanical needs, whether you\'re working on cars, bikes, or household repairs.',
                'price' => 1299, // $12.99 in cents
                'img' => '/assets/wrench.jpg',
                'imgcropped' => '/assets/wrench-cropped.jpg'
            ],
            [
                'title' => 'Nails',
                'description' => 'High-quality steel nails for construction',
                'descriptionfull' => 'These premium steel nails are perfect for all your construction and carpentry projects. Available in various sizes, they provide excellent holding power and durability.',
                'price' => 899, // $8.99 in cents
                'img' => '/assets/nails.jpg',
                'imgcropped' => '/assets/nails-cropped.jpg'
            ],
            [
                'title' => 'Hammer',
                'description' => 'Professional-grade hammer for heavy-duty work',
                'descriptionfull' => 'This professional-grade hammer features a balanced design with a comfortable handle and hardened steel head. Ideal for both professional contractors and DIY enthusiasts.',
                'price' => 2499, // $24.99 in cents
                'img' => '/assets/hammer.jpg',
                'imgcropped' => '/assets/hammer-cropped.jpg'
            ]
        ];

        return $this->faker->randomElement($products);
    }
}
