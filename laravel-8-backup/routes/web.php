<?php

include 'inventory.php';
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Route;
use App\Exceptions\Handler;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Illuminate\Support\Facades\Cache;
use Sentry\State\Scope;
use App\Product;
use App\Review;
use App\Inventory;

function getProductsWithReviews() {
    $complete_product_with_reviews = array();
    $products = Product::all();
    $reviews = DB::select('SELECT reviews.id, products.id AS productid, reviews.rating, reviews.customerId, reviews.description, reviews.created FROM reviews INNER JOIN products ON reviews.productId = products.id');

    foreach ($products as $product) {
        $final_results = array();
        $result = $product;
        $review_array = array();

        $productID = $product->id;

        foreach ($reviews as $review) {
            $review_product_id = $review->productid;

            if ($productID == $review_product_id) {

                array_push($review_array, $review);
            } 
        }
        array_push($final_results, $review_array);
        
        $final_results_array= json_encode($final_results);
        $result['reviews'] = $final_results;
        $final_results= json_encode($result);

        array_push($complete_product_with_reviews, $result);
    }

    return $complete_product_with_reviews;
}

Route::get('/products', ['as' => 'products', function () {
    return getProductsWithReviews();
}]);

Route::get('/products-join', ['as' => 'products-join', function () {
    return getProductsWithReviews();
}]);

Route::get('/handled', ['as' => 'handled', function (Request $request) {
    try {
        throw new Exception("This is a handled exception");
    } catch (\Throwable $exception) {
        report($exception);
    }
    return $exception;
}]);

Route::get('/unhandled', ['as' => 'unhandled', function () {
    1/0;
}]);

Route::post('/checkout', ['as' => 'checkout', function (Request $request) {
    get_inventory();
    throw new Exception("Not enough inventory");
}]);

Route::get('/', function () {
    return view('welcome');
});

Route::get('/success', ['as' => 'success', function () {
    return 'success';
}]);

Route::get('/api', function () {
    return 'laravel /api';
});

Route::get('/organization', function () {
    return 'laravel /organization';
});

Route::get('/connect', function () {
    return 'laravel /connect';
});

Route::get('/debug-sentry', function () {
    throw new Exception('My first Sentry error!');
});

function decrementInventory($item) {
    Cache::decrement($item->id, 1);
}

function get_inventory() {
    $inventory = Inventory::all();
    return $inventory;
}

function isOutOfStock($item) {
    $inventory = get_inventory();
    return $inventory->{$item->id} <= 0;
}

function process_order(array $cart) {
    error_log("IN PROCESS ORDER");
    foreach ($cart as $item) {
        if (isOutOfStock($item)) {
            throw new Exception("Not enough inventory for " . $item->id);
        } else {
            decrementInventory($item);
        }
    }
}

function set_inventory() {
    $tools = array(1 => "wrench", 2 => "nails", 3 => "hammer");
    foreach ($tools as &$tool) {
        if (!Cache::has($tool)) {
            Cache::increment($tool, 1);
        }
    }
}