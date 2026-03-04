<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Jobs\SendEmail;
use App\Services\OrderService;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Log;

class EmailController extends Controller
{
    public function __construct(
        private OrderService $orderService
    ) {}

    /**
     * Get all products with reviews
     * Extracted from the original /products route
     */
    public function enqueue(Request $request): JsonResponse
    {
        Log::info('Received /enqueue endpoint request');

        // Validate the request first
        $request->validate([
            'email' => 'required|email'
        ]);

        $email = $request->input('email');

        // Dispatch the SendEmail job to the queue
        $job = SendEmail::dispatch($email);

        Log::info('Completed /enqueue request - email task enqueued');

        return response()->json(['status' => 'success'], 200);
    }
}
