<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\ProductController;
use App\Http\Controllers\Api\InventoryController;

Route::get('/user', function (Request $request) {
    return $request->user();
})->middleware('auth:sanctum');

// Product routes (extracted from original Laravel 8.x)
Route::get('/products', [ProductController::class, 'index']);
Route::post('/checkout', [ProductController::class, 'checkout']);

// Inventory routes
Route::get('/inventory', [InventoryController::class, 'index']);

// Error testing routes (for Sentry integration)
Route::get('/handled', [ProductController::class, 'handled']);
Route::get('/unhandled', [ProductController::class, 'unhandled']); 