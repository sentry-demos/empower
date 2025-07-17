<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Product;
use App\Services\OrderService;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Str;

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
        $products = Product::with('reviews')->get();
        
        // Transform to match original format
        $completeProductsWithReviews = $products->map(function ($product) {
            $productArray = $product->toArray();
            $productArray['reviews'] = $product->reviews->map(function ($review) {
                return [
                    'id' => $review->id,
                    'productid' => $review->product_id,
                    'rating' => $review->rating,
                    'customerId' => $review->customer_id,
                    'description' => $review->description,
                    'created' => $review->created_at,
                ];
            })->toArray();
            
            return $productArray;
        });

        return response()->json($completeProductsWithReviews);
    }

    /**
     * Process checkout
     * Extracted from the original /checkout route
     */
    public function checkout(Request $request): JsonResponse
    {
        // Get inventory (like original)
        $this->orderService->getInventory();
        
        // Always throw exception like original
        throw new \Exception("Not enough inventory");
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
