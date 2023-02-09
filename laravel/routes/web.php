<?php

include 'inventory.php';
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Route;
use App\Exceptions\Handler;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Illuminate\Support\Facades\Cache;
use Sentry\State\Scope;
use App\Models\Product;
use App\Models\Review;
use App\Models\Inventory;
// use sentry_sdk;

Route::get('/products', ['as' => 'products', function () {
    // TODO Clean up top level array of reviews
    // TODO Rename vars so more clear
    // TODO Refactor into ORM
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

// TODO Write logic here - spoofing to make demo deadline for now
Route::post('/checkout', ['as' => 'checkout', function (Request $request) {
    // try {
    //     app('sentry')->configureScope(static function (Scope $scope) use ($request): void {
    //         $payload = $request->getContent();
    //         $order = json_decode($payload);
    //         $email = $order->email;
    //         $cart = $order->cart;
    //         $scope->setUser(['email' => $email]);
    //         $scope->setTags(["transaction_id" => $request->header('X-Transaction-ID')]);
    //         $scope->setTags(["session-id" => $request->header('X-Session-Id')]);
    //         $scope->setExtra("order", $cart);
    //         process_order($order->cart);
    //     });
    // } catch (Exception $e) {
    //     report($e);
    // return response("Internal Server Error", 500)->header("HTTP/1.1 500", "")->header('Content-Type', "text/html");
    // }
    // $products = Product::all();
    get_inventory();
    throw new Exception("Not enough inventory");
}]);

Route::get('/', function () {
    return view('welcome');
});

Route::get('/success', ['as' => 'success', function () {
    return 'success';
}]);

//TODO Determine functionality of these routes
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

// TODO Refactor functions into own files/modules/controllers TBD
function decrementInventory($item) {
    Cache::decrement($item->id, 1);
}

function get_inventory() {
    // Get quantity of items in cart
    // Get product ids off items in cart
    // Store product ids in array
    // $products = Product::all();
    $inventory = Inventory::all();
//     sentry_sdk.start_span(op="get_inventory", description="db.connect"):
//     connection = db.connect()
// with sentry_sdk.start_span(op="get_inventory", description="db.query") as span:
//     inventory = connection.execute(
//         "SELECT * FROM inventory WHERE productId in %s" % (productIds)
//     ).fetchall()

    // $inventory = new StdClass();
    // $inventory->wrench = Cache::get('wrench');
    // $inventory->nails = Cache::get('nails');
    // $inventory->hammer = Cache::get('hammer');
    
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