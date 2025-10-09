<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\ProductController;

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
    return 'laravel /organization';
});
Route::get('/connect', function () {
    return 'laravel /connect';
});
Route::get('/debug-sentry', function () {
    throw new Exception('My first Sentry error!');
});
