<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Inventory;

class InventorySeeder extends Seeder
{
    /**
     * Run the database seeds.
     *
     * @return void
     */
    public function run()
    {
        $products = [
            ['id' => 1, 'quantity' => 10], // wrench
            ['id' => 2, 'quantity' => 10], // nails
            ['id' => 3, 'quantity' => 10]  // hammer
        ];

        foreach ($products as $product) {
            Inventory::create(['product_id' => $product['id'], 'quantity' => $product['quantity']]);
        }
    }
}