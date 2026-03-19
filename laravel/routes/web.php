<?php

use App\Http\Controllers\Api\EmailController;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\ProductController;

Route::get('/', function () {
    return view('welcome');
});

// Web routes matching original Laravel 8.x implementation
Route::get('/products', [ProductController::class, 'products']);
Route::get('/products-join', [ProductController::class, 'products_join']); // Optimized with JOIN queries
Route::post('/checkout', [ProductController::class, 'checkout']);
Route::get('/handled', [ProductController::class, 'handled']);
Route::get('/unhandled', [ProductController::class, 'unhandled']);
Route::get('/success', function () {
    Log::info('Received /success endpoint request');
    Log::info('Completed /success request');
    return 'success';
});
Route::get('/api', function () {
    Log::info('Received /api endpoint request');
    return 'laravel /api';
});
Route::get('/organization', function () {
    Log::info('Received /organization endpoint request');
    return 'laravel /organization';
});
Route::get('/connect', function () {
    Log::info('Received /connect endpoint request');
    return 'laravel /connect';
});
Route::post('/apply-promo-code', [ProductController::class, 'apply_promo_code']);
Route::get('/product/0/info', [ProductController::class, 'product_info']);
Route::get('/debug-sentry', function () {
    throw new Exception('My first Sentry error!');
});

// Cache testing routes (for Sentry integration)
Route::get('/maybe-cached', [ProductController::class, 'maybe_cached']);

// Email routes, testing async jobs
Route::post('/enqueue', [EmailController::class, 'enqueue']); 