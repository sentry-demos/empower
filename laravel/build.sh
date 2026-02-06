#!/bin/bash

set -e

# =============================================================================
# PHP Version Check
# This project requires PHP 8.3.x. Fail fast if a different version is used.
# =============================================================================
REQUIRED_PHP_MAJOR_MINOR="8.3"
CURRENT_PHP_VERSION=$(php -r 'echo PHP_MAJOR_VERSION . "." . PHP_MINOR_VERSION;')

if [[ "$CURRENT_PHP_VERSION" != "$REQUIRED_PHP_MAJOR_MINOR" ]]; then
    echo "ERROR: PHP version mismatch!"
    echo "  Required: PHP ${REQUIRED_PHP_MAJOR_MINOR}.x"
    echo "  Current:  PHP $(php -r 'echo PHP_VERSION;')"
    echo ""
    echo "Please install PHP ${REQUIRED_PHP_MAJOR_MINOR}.x or update the version requirements in:"
    echo "  - laravel/composer.json (require.php and config.platform.php)"
    echo "  - .github/workflows/auto-deploy.yml (setup-php php-version)"
    exit 1
fi

echo "PHP version check passed: $(php -r 'echo PHP_VERSION;')"

# =============================================================================
# Install dependencies
# Using --no-scripts to work around Laravel 12 bug where package:discover
# fails with "Call to a member function make() on null" during composer install.
# See: https://github.com/laravel/framework/issues/56098
# =============================================================================
composer install --no-scripts

# Run composer scripts manually (except package:discover which has the bug)
composer dump-autoload --optimize

php artisan optimize:clear
php artisan optimize

php artisan config:cache
php artisan route:cache
php artisan view:cache
php artisan event:cache