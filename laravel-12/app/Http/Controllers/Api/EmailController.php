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
    public function enqueue(): JsonResponse
    {
        // Validate the request first
        $request->validate([
            'email' => 'required|email'
        ]);

        $email = $request->input('email');

        // Dispatch the SendEmail job to the queue
        $job = SendEmail::dispatch($email);

        // Log the job dispatch (Laravel doesn't expose task_id like Celery, but we can log the job)
        Log::info("Email job dispatched for email: {$email}");

        return response()->json(['status' => 'success'], 200);
    }
}
