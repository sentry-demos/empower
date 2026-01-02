<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Product;
use App\Services\OrderService;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Str;
use Illuminate\Support\Facades\DB;
use Exception;

class ProductController extends Controller
{
    public function __construct(
        private OrderService $orderService
    ) {}

    /**
     * Get all products with reviews
     * Extracted from the original /products route
     */
    public function index(): JsonResponse
    {
        // Generate random number to determine cache key strategy
        $randomValue = rand(0, 99);
        
        // in 50% of cases, use a random cache key so that we will have a cache miss
        if ($randomValue < 50) {
            $cacheKey = 'products-random-' . Str::random(16);
        } else {
            $cacheKey = 'products-cached';
        }
        
        // Attempt to retrieve from cache
        $cachedData = Cache::get($cacheKey);
        
        if ($cachedData !== null) {
            // Cache hit - return cached data
            return response()->json($cachedData);
        }
        
        // Cache miss - fetch from database
        $products = Product::with('reviews')->get();
        
        // Transform to match original format
        $completeProductsWithReviews = $products->map(function ($product) {
            $productArray = $product->toArray();
            $productArray['reviews'] = $product->reviews->map(function ($review) {
                return [
                    'id' => $review->id,
                    'productid' => $review->productid,
                    'rating' => $review->rating,
                    'customerId' => $review->customerid,
                    'description' => $review->description,
                    'created' => $review->created,
                ];
            })->toArray();
            
            return $productArray;
        })->toArray();
        
        // Store in cache (1 hour TTL for fixed key, random keys will never be retrieved anyway)
        Cache::put($cacheKey, $completeProductsWithReviews, 3600);

        return response()->json($completeProductsWithReviews);
    }

    /**
     * Process checkout
     * Extracted from the original /checkout route
     */
    public function checkout(Request $request): JsonResponse
    {
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
    }

    /**
     * Handle exceptions for testing
     * Extracted from the original /handled route
     */
    public function handled(): JsonResponse
    {
        try {
            throw new \Exception("This is a handled exception");
        } catch (\Throwable $exception) {
            report($exception);
            return response()->json([
                'message' => $exception->getMessage(),
                'handled' => true
            ]);
        }
    }

    /**
     * Unhandled exception for testing
     * Extracted from the original /unhandled route
     */
    public function unhandled(): void
    {
        // This will throw a division by zero error
        1/0;
    }

    /**
     * 
     */
    public function maybe_cached(): JsonResponse
    {
        Cache::rememberForever('always-cached-key', fn () => Str::random(16));
        $randomValue = rand(0, 4);
        if ($randomValue === 0) {
            $value = Cache::get('never-cached-key');
            $cached = false;
        } else {
            $value = Cache::get('always-cached-key');
            $cached = true;
        }

        return response()->json([
            'value' => $value,
            'cached' => $cached
        ]);
    }
}



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