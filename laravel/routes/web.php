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
    $order = json_decode($request->getContent(), true);
    $cart = $order["cart"];
    $form = $order["form"];
    $validate_inventory = true;
    if (isset($order["validate_inventory"])) {
        $validate_inventory = $order["validate_inventory"] == "true";
    }
    
    $inventory = [];
    try {
        $inventory = get_inventory($cart);
        // id | sku | count | productid
    } catch (Exception $err) {
        throw $err;
    }
    
    error_log("> /checkout inventory " . json_encode($inventory));
    error_log("> validate_inventory " . ($validate_inventory ? "true" : "false"));
    
    $fulfilled_count = 0;
    $out_of_stock = []; // list of items that are out of stock
    try {
        if ($validate_inventory) {
            if (empty($quantities)) {
                throw new Exception("Invalid checkout request: cart is empty");
            }
            
            $quantities = [];
            foreach ($cart['quantities'] as $key => $value) {
                $quantities[(int)$key] = $value;
            }
            $inventory_dict = [];
            foreach ($inventory as $x) {
                $inventory_dict[$x->productid] = $x;
            }
            
            foreach ($quantities as $product_id => $quantity) {
                $inventory_count = isset($inventory_dict[$product_id]) ? $inventory_dict[$product_id]->count : 0;
                if ($inventory_count >= $quantity) {
                    decrement_inventory($inventory_dict[$product_id]->id, $quantity);
                    $fulfilled_count += 1;
                } else {
                    $title = null;
                    foreach ($cart['items'] as $item) {
                        if ($item['id'] == $product_id) {
                            $title = $item['title'];
                            break;
                        }
                    }
                    $out_of_stock[] = $title;
                }
            }
        }
    } catch (Exception $err) {
        throw new Exception("Error validating enough inventory for product", 0, $err);
    }
    
    if (empty($out_of_stock)) {
        $result = ['status' => 'success'];
        error_log("Checkout successful");
    } else {
        // react doesn't handle these yet, shows "Checkout complete" as long as it's HTTP 200
        if ($fulfilled_count == 0) {
            $result = ['status' => 'failed']; // All items are out of stock
        } else {
            $result = ['status' => 'partial', 'out_of_stock' => $out_of_stock];
        }
    }
    
    return response()->json($result);
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

function decrement_inventory($product_id, $count) {
    // Do nothing
}

function get_inventory($cart) {
    error_log("> get_inventory");
    
    $quantities = $cart['quantities'];
    
    error_log("> quantities " . json_encode($quantities));
    
    $productIds = [];
    foreach (array_keys($quantities) as $productId_str) {
        error_log("Processing product ID: " . $productId_str);
        $productIds[] = intval($productId_str);
    }
    
    error_log("> productIds " . json_encode($productIds));
    
    try {
        $inventory = DB::select('SELECT * FROM inventory WHERE productid IN (' . implode(',', array_fill(0, count($productIds), '?')) . ')', $productIds);
    } catch (Exception $err) {
        throw new Exception('get_inventory', 0, $err);
    }
    
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