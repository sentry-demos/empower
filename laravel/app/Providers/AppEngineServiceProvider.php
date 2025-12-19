

<?php
namespace App\Providers;

use Illuminate\Support\ServiceProvider;

class AppEngineServiceProvider extends ServiceProvider
{
    public function boot()
    {
        // Set up writable directories on App Engine
        $this->setupTmpDirectories();
        $this->configureStoragePath();
    }

    private function setupTmpDirectories()
    {
        $directories = [
            '/tmp/app/',
            '/tmp/app/public',
            '/tmp/framework/',
            '/tmp/framework/cache/data',
            '/tmp/framework/sessions',
            '/tmp/framework/views',
            '/tmp/logs',
        ];

        foreach ($directories as $directory) {
            if (!file_exists($directory)) {
                mkdir($directory, 0755, true);
            }
        }
    }

    private function configureStoragePath()
    {
        // Override Laravel's storage path
        $this->app->useStoragePath('/tmp/storage');
    }
}

