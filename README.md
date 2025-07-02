<p align="center"><a href="https://laravel.com" target="_blank"><img src="https://raw.githubusercontent.com/laravel/art/master/logo-lockup/5%20SVG/2%20CMYK/1%20Full%20Color/laravel-logolockup-cmyk-red.svg" width="400" alt="Laravel Logo"></a></p>

<p align="center">
<a href="https://github.com/laravel/framework/actions"><img src="https://github.com/laravel/framework/workflows/tests/badge.svg" alt="Build Status"></a>
<a href="https://packagist.org/packages/laravel/framework"><img src="https://img.shields.io/packagist/dt/laravel/framework" alt="Total Downloads"></a>
<a href="https://packagist.org/packages/laravel/framework"><img src="https://img.shields.io/packagist/v/laravel/framework" alt="Latest Stable Version"></a>
<a href="https://packagist.org/packages/laravel/framework"><img src="https://img.shields.io/packagist/l/laravel/framework" alt="License"></a>
</p>

## About Laravel

Laravel is a web application framework with expressive, elegant syntax. We believe development must be an enjoyable and creative experience to be truly fulfilling. Laravel takes the pain out of development by easing common tasks used in many web projects, such as:

- [Simple, fast routing engine](https://laravel.com/docs/routing).
- [Powerful dependency injection container](https://laravel.com/docs/container).
- Multiple back-ends for [session](https://laravel.com/docs/session) and [cache](https://laravel.com/docs/cache) storage.
- Expressive, intuitive [database ORM](https://laravel.com/docs/eloquent).
- Database agnostic [schema migrations](https://laravel.com/docs/migrations).
- [Robust background job processing](https://laravel.com/docs/queues).
- [Real-time event broadcasting](https://laravel.com/docs/broadcasting).

Laravel is accessible, powerful, and provides tools required for large, robust applications.

## Learning Laravel

Laravel has the most extensive and thorough [documentation](https://laravel.com/docs) and video tutorial library of all modern web application frameworks, making it a breeze to get started with the framework.

You may also try the [Laravel Bootcamp](https://bootcamp.laravel.com), where you will be guided through building a modern Laravel application from scratch.

If you don't feel like reading, [Laracasts](https://laracasts.com) can help. Laracasts contains thousands of video tutorials on a range of topics including Laravel, modern PHP, unit testing, and JavaScript. Boost your skills by digging into our comprehensive video library.

## Laravel Sponsors

We would like to extend our thanks to the following sponsors for funding Laravel development. If you are interested in becoming a sponsor, please visit the [Laravel Partners program](https://partners.laravel.com).

### Premium Partners

- **[Vehikl](https://vehikl.com)**
- **[Tighten Co.](https://tighten.co)**
- **[Kirschbaum Development Group](https://kirschbaumdevelopment.com)**
- **[64 Robots](https://64robots.com)**
- **[Curotec](https://www.curotec.com/services/technologies/laravel)**
- **[DevSquad](https://devsquad.com/hire-laravel-developers)**
- **[Redberry](https://redberry.international/laravel-development)**
- **[Active Logic](https://activelogic.com)**

## Contributing

Thank you for considering contributing to the Laravel framework! The contribution guide can be found in the [Laravel documentation](https://laravel.com/docs/contributions).

## Code of Conduct

In order to ensure that the Laravel community is welcoming to all, please review and abide by the [Code of Conduct](https://laravel.com/docs/contributions#code-of-conduct).

## Security Vulnerabilities

If you discover a security vulnerability within Laravel, please send an e-mail to Taylor Otwell via [taylor@laravel.com](mailto:taylor@laravel.com). All security vulnerabilities will be promptly addressed.

## License

The Laravel framework is open-sourced software licensed under the [MIT license](https://opensource.org/licenses/MIT).

# Laravel 12.x Demo Application

This is a modernized e-commerce demo application built with Laravel 12.x, part of the empower multi-framework demonstration repository.

## Features

- **Products**: Browse and manage product catalog
- **Reviews**: Product review system with ratings
- **Inventory**: Real-time inventory management with caching
- **Checkout**: Order processing with stock validation
- **Error Monitoring**: Sentry integration for error tracking
- **CORS Support**: Cross-origin resource sharing for API access

## Requirements

- PHP 8.2+
- Composer
- SQLite (default) or PostgreSQL
- Google App Engine (for deployment)

## Quick Start

### Local Development

1. **Install Dependencies**
   ```bash
   composer install
   ```

2. **Environment Setup**
   ```bash
   cp .env.example .env
   php artisan key:generate
   ```

3. **Database Setup**
   ```bash
   php artisan migrate
   php artisan db:seed
   ```

4. **Run Development Server**
   ```bash
   php artisan serve
   ```

### Google App Engine Deployment

1. **Configure Environment**
   ```bash
   export SERVICE=laravel-demo
   ```

2. **Deploy Application**
   ```bash
   ./build.sh
   gcloud app deploy app.yaml
   ```

## Architecture

### Laravel 12.x Structure

```
app/
├── Http/
│   ├── Controllers/        # API Controllers
│   └── Middleware/         # Custom middleware
├── Models/                 # Eloquent models
└── Services/              # Business logic services

routes/
├── api.php                # API routes
└── web.php                # Web routes

database/
├── migrations/            # Database migrations
├── seeders/              # Data seeders
└── factories/            # Model factories
```

### Business Logic Organization

- **Controllers**: Handle HTTP requests and responses
- **Services**: Core business logic (inventory, orders)
- **Models**: Data layer with proper relationships
- **Middleware**: Cross-cutting concerns (CORS, auth)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products` | List all products with reviews |
| POST | `/api/checkout` | Process order and validate inventory |
| GET | `/api/inventory` | Get current inventory levels |
| GET | `/api/handled` | Test handled exception |
| GET | `/api/unhandled` | Test unhandled exception |

## Configuration

### Environment Variables

```env
APP_NAME=Laravel
APP_ENV=production
APP_KEY=base64:...
APP_DEBUG=false
APP_URL=https://your-app.appspot.com

DB_CONNECTION=sqlite
DB_DATABASE=/path/to/database.sqlite

SENTRY_LARAVEL_DSN=your-sentry-dsn
```

### Google App Engine

The application is configured to run on Google App Engine with:
- **Runtime**: PHP 8.3
- **Storage**: `/tmp` directory for temporary files
- **Scaling**: Manual scaling with 1 instance

## Development Phases

This application was built using a phased approach:

### Phase 1: Foundation ✅
- [x] Laravel 12.x installation
- [x] Dependencies (Sentry, CORS)  
- [x] Google App Engine configuration
- [x] Basic middleware setup

### Phase 2: Database & Models (In Progress)
- [ ] Create migrations for products, reviews, inventory
- [ ] Build Eloquent models with relationships
- [ ] Set up model factories and seeders

### Phase 3: Business Logic Extraction
- [ ] Extract business logic from legacy routes
- [ ] Create service classes
- [ ] Build proper controllers

### Phase 4: API & Testing
- [ ] Implement RESTful API routes
- [ ] Add comprehensive testing
- [ ] Performance optimization

### Phase 5: Deployment & Documentation
- [ ] Production deployment
- [ ] Performance monitoring
- [ ] Final documentation

## Migration from Laravel 8.x

This application replaces the legacy Laravel 8.x demo with modern practices:

**Improvements:**
- ✅ **Laravel 12.x**: Latest framework version with type safety
- ✅ **Proper Architecture**: MVC separation of concerns
- ✅ **Modern Dependencies**: Updated package versions
- ✅ **Clean Structure**: No business logic in routes
- ✅ **Type Safety**: Full type hints throughout

**Legacy Issues Fixed:**
- ❌ Business logic mixed in routes
- ❌ No proper controller structure  
- ❌ Outdated dependencies
- ❌ Missing type safety

## Contributing

1. Follow Laravel coding standards
2. Use proper type hints
3. Write comprehensive tests
4. Update documentation

## Support

- **Framework**: Laravel 12.x (supported until Q1 2027)
- **PHP**: 8.2+ (active support)
- **Dependencies**: Latest stable versions

---

Part of the [Empower Multi-Framework Demo](../README.md) repository showcasing modern web development patterns across different frameworks.
