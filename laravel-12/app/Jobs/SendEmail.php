<?php

namespace App\Jobs;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldBeUnique;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Log;
use Exception;

class SendEmail implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public $tries = 5; // Maximum number of retries
    public $backoff = 10; // Seconds to wait before retry

    protected $email;

    /**
     * Create a new job instance.
     *
     * @param string $email
     * @return void
     */
    public function __construct($email)
    {
        $this->email = $email;
    }

    /**
     * Execute the job.
     *
     * @return void
     */
    public function handle()
    {
        try {
            // Simulate random error (20% chance - same as Python randrange(5) == 0)
            $randomValue = rand(0, 4);
            if ($randomValue === 0) {
                throw new Exception("sending email error");
            }

            // Sleep for random amount of time (0-4 seconds)
            sleep($randomValue);

            // Log the email being sent
            Log::info("Sending email to: " . $this->email);

            return $randomValue;
        } catch (Exception $e) {
            // If we haven't exceeded max retries, throw the exception to trigger retry
            if ($this->attempts() < $this->tries) {
                throw $e;
            }
            
            // If we've exceeded max retries, log the final failure
            Log::error("Failed to send email to {$this->email} after {$this->tries} attempts: " . $e->getMessage());
            throw $e;
        }
    }

    /**
     * Handle a job failure.
     *
     * @param Exception $exception
     * @return void
     */
    public function failed(Exception $exception)
    {
        Log::error("SendEmail job failed for {$this->email}: " . $exception->getMessage());
    }
}
