<?php

use Illuminate\Support\Facades\Route;
use Illuminate\Support\Facades\Cache;

use App\Http\Controllers\Api\EmailController;
use App\Http\Controllers\Api\ProductController;
use App\Models\Product;

Route::get('/', function () {
    return view('welcome');
});

// Web routes matching original Laravel 8.x implementation
Route::get('/products', [ProductController::class, 'index']);
Route::get('/products-join', [ProductController::class, 'index']); // Same as products for now
Route::post('/checkout', [ProductController::class, 'checkout']);
Route::get('/handled', [ProductController::class, 'handled']);
Route::get('/unhandled', [ProductController::class, 'unhandled']);
Route::get('/success', function () {
    return 'success';
});
Route::get('/api', function () {
    return 'laravel /api';
});
Route::get('/organization', function () {
    return Cache::remember('laravel.cache.organization', 1000, function () {
        // perform products db query 1% of time in order
        // to populate "Found In" endpoints in Queries
        if (rand(0, 100) == 0) {
            Product::with('reviews')->get();
        }
        return 'laravel /organization';
    });
});
Route::get('/connect', function () {
    return 'laravel /connect';
});
Route::get('/debug-sentry', function () {
    throw new Exception('My first Sentry error!');
});
Route::get('/enqueue', [EmailController::class, 'enqueue']);
