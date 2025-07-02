<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\OrderService;
use Illuminate\Http\JsonResponse;

class InventoryController extends Controller
{
    public function __construct(
        private OrderService $orderService
    ) {}

    /**
     * Get all inventory levels
     * Extracted from the original get_inventory() function
     */
    public function index(): JsonResponse
    {
        $inventory = $this->orderService->getInventory();
        
        return response()->json($inventory);
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        //
    }

    /**
     * Display the specified resource.
     */
    public function show(string $id)
    {
        //
    }

    /**
     * Update the specified resource in storage.
     */
    public function update(Request $request, string $id)
    {
        //
    }

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(string $id)
    {
        //
    }
}
