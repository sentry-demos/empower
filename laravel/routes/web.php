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

Route::get('/products', ['as' => 'products', function () {
    $products = Product::all();

    foreach ($products as $product) {
        // TODO: join review results from query with products
        $review = Review::find($product->id);
        
        $review_json_output = json_encode($review);
        echo "review decode output", $review_json_output;

    }
    return $products;
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
    try {
        app('sentry')->configureScope(static function (Scope $scope) use ($request): void {
            $payload = $request->getContent();
            $order = json_decode($payload);
            $email = $order->email;
            $cart = $order->cart;
            $scope->setUser(['email' => $email]);
            $scope->setTags(["transaction_id" => $request->header('X-Transaction-ID')]);
            $scope->setTags(["session-id" => $request->header('X-Session-Id')]);
            $scope->setExtra("order", $cart);
            process_order($order->cart);
        });

    } catch (Exception $e) {
        report($e);
        return response("Internal Server Error", 500)->header("HTTP/1.1 500", "")->header('Content-Type', "text/html");
    }
}]);

function decrementInventory($item) {
    Cache::decrement($item->id, 1);
}

function get_inventory() {
    $inventory = new StdClass();
    $inventory->wrench = Cache::get('wrench');
    $inventory->nails = Cache::get('nails');
    $inventory->hammer = Cache::get('hammer');
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

Route::get('/', function () {
    return view('welcome');
});

Route::get('/success', ['as' => 'success', function () {
    return 'success';
}]);