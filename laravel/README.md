# sentry-demos/laravel

Moved from old repository: https://github.com/sentry-demos/laravel

## Overview
To show how Sentry works in an example web app that uses PHP Laravel

Demonstrates:
- Import/integrate SDK into project
- Configuration
- Releases/Commits
- Event management

**Official Sentry documentation** found here:
https://docs.sentry.io/platforms/php/laravel/

Trigger an error that gets sent as Event to Sentry.io Platform
web.php has multiple endpoints for showing different ways that errors are handled

## Setup
#### Versions

| dependency      | version           
| ------------- |:-------------:| 
| sentry-laravel   | 2.2.0    |
| sentry-cli   | 1.53.0    |
| laravel | 8.0      |
| php   | 7.2.5     |

## First-time Setup
1. Install [php](https://www.php.net/downloads)
2. Install [Composer](https://getcomposer.org/download/)
3. Install [Laravel](composer global require laravel/installer)
4. Install [artisan](https://github.com/artisan-roaster-scope/artisan/releases/tag/v2.8.2)
5. In `laravel` folder, run `composer install` to install dependencies from `composer.json`
6. Set your DSN key, projectID, and Sentry OrganizationID in `.env`
7. Run `./deploy.sh --env=local react laravel` to spin up both the React FE + Laravel BE
8. Configure Sentry based on [Laravel SDK docs](https://docs.sentry.io/platforms/php/guides/laravel/) including confirming the "My first Sentry error!" Exception is thrown in Sentry by hitting the `/debug-sentry' endpoint (described in the docs).
9. Use `http://localhost:8000/handled` and `http://localhost:8000/unhandled` to trigger errors

## Tips
* If you are noticing changes aren't being picked up by your app or any other unexpected behavior, try clearing your cache with: `php artisan cache:clear`
* For more information about the ORM being used, check out [Eloquent ORM](https://laravel.com/docs/5.0/eloquent#introduction)

## Technical Notes or Troubleshooting
This demo leverages log channels to record more info and allow you
to configure the log level in `logging.php`.
The minimum event level is set to `debug` by default which may be
too verbose. 

# GIF

![Alt Text](overview.gif)
