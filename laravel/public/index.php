<?php

/**
 * Laravel - A PHP Framework For Web Artisans
 *
 * @package  Laravel
 * @author   Taylor Otwell <taylor@laravel.com>
 */

# [START] Add the following block to `public/index.php`
/*
|--------------------------------------------------------------------------
| GCP App Engine Writable Directories
|--------------------------------------------------------------------------
|
| Before we start up Laravel, let's check if we are running in GCP App Engine,
| and, if so, make sure that the Laravel's storage directory structure is
| present.
|
*/

if (getenv('IS_APP_ENGINE')
    && !file_exists('/tmp/.dirs_created')) {
    foreach (['/tmp/app/public',
                '/tmp/framework/cache/data',
                '/tmp/framework/sessions',
                '/tmp/framework/testing',
                '/tmp/framework/views',
                '/tmp/logs'] as $tmpdir) {
        if (!file_exists($tmpdir)) {
            mkdir($tmpdir, 0755, true);
        }
    }
    touch('/tmp/.dirs_created');
}
# [END]


define('LARAVEL_START', microtime(true));

/*
|--------------------------------------------------------------------------
| Register The Auto Loader
|--------------------------------------------------------------------------
|
| Composer provides a convenient, automatically generated class loader for
| our application. We just need to utilize it! We'll simply require it
| into the script here so that we don't have to worry about manual
| loading any of our classes later on. It feels great to relax.
|
*/

require __DIR__.'/../vendor/autoload.php';

/*
|--------------------------------------------------------------------------
| Turn On The Lights
|--------------------------------------------------------------------------
|
| We need to illuminate PHP development, so let us turn on the lights.
| This bootstraps the framework and gets it ready for use, then it
| will load up this application so that we can run it and send
| the responses back to the browser and delight our users.
|
*/

$app = require_once __DIR__.'/../bootstrap/app.php';

/*
|--------------------------------------------------------------------------
| Run The Application
|--------------------------------------------------------------------------
|
| Once we have the application, we can handle the incoming request
| through the kernel, and send the associated response back to
| the client's browser allowing them to enjoy the creative
| and wonderful application we have prepared for them.
|
*/

$kernel = $app->make(Illuminate\Contracts\Http\Kernel::class);

$response = $kernel->handle(
    $request = Illuminate\Http\Request::capture()
);

$response->send();

$kernel->terminate($request, $response);
