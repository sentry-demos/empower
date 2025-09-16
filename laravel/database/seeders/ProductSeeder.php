<?php

namespace Database\Seeders;

use App\Models\Product;
use App\Models\Review;
use App\Models\Inventory;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class ProductSeeder extends Seeder
{
    /**
     * Run the database seeds.
     */
    public function run(): void
    {
        // Create the three main products
        $products = [
            [
                'title' => 'Wrench',
                'description' => 'A essential tool for any toolbox',
                'descriptionfull' => 'This high-quality wrench is made from durable steel and features a comfortable grip handle. Perfect for all your mechanical needs, whether you\'re working on cars, bikes, or household repairs.',
                'price' => 1299, // $12.99 in cents
                'img' => '/assets/wrench.jpg',
                'imgcropped' => '/assets/wrench-cropped.jpg',
                'sku' => 'WRN001',
                'stock' => 15
            ],
            [
                'title' => 'Nails',
                'description' => 'High-quality steel nails for construction',
                'descriptionfull' => 'These premium steel nails are perfect for all your construction and carpentry projects. Available in various sizes, they provide excellent holding power and durability.',
                'price' => 899, // $8.99 in cents
                'img' => '/assets/nails.jpg',
                'imgcropped' => '/assets/nails-cropped.jpg',
                'sku' => 'NAL001',
                'stock' => 50
            ],
            [
                'title' => 'Hammer',
                'description' => 'Professional-grade hammer for heavy-duty work',
                'descriptionfull' => 'This professional-grade hammer features a balanced design with a comfortable handle and hardened steel head. Ideal for both professional contractors and DIY enthusiasts.',
                'price' => 2499, // $24.99 in cents
                'img' => '/assets/hammer.jpg',
                'imgcropped' => '/assets/hammer-cropped.jpg',
                'sku' => 'HAM001',
                'stock' => 8
            ]
        ];

        foreach ($products as $productData) {
            // Extract stock info
            $sku = $productData['sku'];
            $stock = $productData['stock'];
            unset($productData['sku'], $productData['stock']);

            // Create product
            $product = Product::create($productData);

            // Create inventory
            Inventory::create([
                'sku' => $sku,
                'count' => $stock,
                'product_id' => $product->id,
            ]);

            // Create 3-7 reviews per product
            $reviewCount = rand(3, 7);
            Review::factory($reviewCount)->create([
                'product_id' => $product->id,
            ]);
        }
    }
}
