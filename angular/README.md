# Angular Frontend Application

A modern Angular 20 application that demonstrates Sentry error monitoring and performance tracking, designed to be compatible with Test-Driven Automation (TDA) tests.

## 🚀 **Quick Start**

### **Prerequisites**
- Node.js 24.6.0+ (use `.nvmrc` for exact version)
- npm 11.5.1+
- Angular CLI 20.0.0+

### **Local Development**
```bash
# Install dependencies
npm install

# Start development server (UI-focused, uses localhost backends)
npm start

# Build for production
npm run build
```

### **Using Deploy Script (Recommended)**
```bash
# Deploy Angular with default Flask backend
./deploy angular --env=local

# Deploy Angular with specific backend
./deploy angular laravel --env=local
./deploy angular express --env=local
./deploy angular springboot --env=local
./deploy angular aspnetcore --env=local
./deploy angular rails --env=local

# Deploy to staging
./deploy angular --env=staging

# Deploy to production
./deploy angular --env=production
```

## 🌐 **Backend Support**

### **Supported Backends (6 total)**
- **Flask** (default) - Python web framework
- **Express** - Node.js web framework  
- **Spring Boot** - Java web framework
- **ASP.NET Core** - .NET web framework
- **Laravel** - PHP web framework
- **Ruby on Rails** - Ruby web framework

### **Backend URLs**
- **Local**: `http://localhost:8080` (Flask), `http://localhost:8088` (Express), etc.
- **Staging**: `https://staging-flask.empower-plant.com`, `https://staging-express.empower-plant.com`, etc.
- **Production**: `https://flask.empower-plant.com`, `https://express.empower-plant.com`, etc.

### **Backend Switching**
The application supports dynamic backend switching via URL parameters:

```bash
# Use Flask (default)
http://localhost:4200/

# Switch to different backends
http://localhost:4200/?backend=laravel
http://localhost:4200/?backend=express
http://localhost:4200/?backend=springboot
http://localhost:4200/?backend=aspnetcore
http://localhost:4200/?backend=rails

# Combine with other parameters
http://localhost:4200/?backend=laravel&se=wassim
```

## 🔧 **Key Features**

### **Sentry Integration**
- **Error Monitoring**: Automatic error capture and reporting
- **Performance Tracking**: Page load and API call performance
- **Session Replay**: User interaction recording
- **Console Logging**: All console logs sent to Sentry
- **SE Tagging**: Support for sales engineer identification (`?se=wassim`)

### **TDA Compatibility**
- **Button Selectors**: Match React application exactly
- **Component Structure**: Identical layout and behavior
- **Error Handling**: Same error scenarios and responses
- **Demo Features**: Identical demo functionality

### **Backend Flexibility**
- **Multiple Backends**: Support for all 6 backends (Flask, Express, Spring Boot, ASP.NET Core, Laravel, Ruby on Rails)
- **Dynamic Switching**: Runtime backend selection via URL parameters
- **Environment Aware**: Automatic configuration per environment (local, staging, production)
- **Deploy Script Integration**: Seamless deployment workflow with backend selection

## 🏗️ **Project Structure**

```
src/
├── app/
│   ├── components/          # UI components
│   │   ├── cart/           # Shopping cart functionality
│   │   ├── checkout/       # Checkout process
│   │   ├── home/           # Homepage
│   │   ├── products/       # Product listing
│   │   └── three-dots/     # Loading animation
│   ├── services/           # Business logic
│   │   ├── cart.service.ts # Cart management
│   │   ├── config.service.ts # Configuration & backend switching
│   │   └── products.service.ts # Product data
│   └── utils/              # Utility functions
│       ├── backend-router.ts # Backend selection and URL resolution
│       ├── errors.ts       # Error handling utilities
│       └── sentry-utils.ts # Sentry helper functions
├── environments/            # Environment configuration
│   ├── environment.ts      # Production builds (webpack injection)
│   └── environment.development.ts # Development builds (localhost backends)
└── assets/                 # Static assets
```

## 🚀 **Deployment**

### **Deploy Script Integration**

The deploy script provides automated deployment with environment variable management:

1. **Project Detection**: Recognizes `angular` as a frontend project
2. **Environment Setup**: Reads configuration from `env-config/{env}.env`
3. **Backend Configuration**: Sets backend URLs based on specified backends
4. **Build Process**: Runs Angular build with configured environment
5. **Local Deployment**: Starts local server for development

### **Backend Priority**
1. **Specified Backends**: If `./deploy angular laravel` is used, Laravel backend is configured
2. **Default Backend**: Flask is always set as default backend
3. **Runtime Switching**: Users can switch between all 6 backends via URL parameters

### **Environment Variables**

The deploy script automatically sets these environment variables for all backends:

#### **Local Environment**
```bash
BACKEND_URL_FLASK=http://localhost:8080
BACKEND_URL_EXPRESS=http://localhost:8088
BACKEND_URL_SPRINGBOOT=http://localhost:8090
BACKEND_URL_ASPNETCORE=http://localhost:8091
BACKEND_URL_LARAVEL=http://localhost:8000
BACKEND_URL_RUBYONRAILS=http://localhost:5000
```

#### **Staging Environment**
```bash
BACKEND_URL_FLASK=https://staging-flask.empower-plant.com
BACKEND_URL_EXPRESS=https://staging-express.empower-plant.com
BACKEND_URL_SPRINGBOOT=https://staging-springboot.empower-plant.com
BACKEND_URL_ASPNETCORE=https://staging-aspnetcore.empower-plant.com
BACKEND_URL_LARAVEL=https://staging-laravel.empower-plant.com
BACKEND_URL_RUBYONRAILS=https://staging-rails.empower-plant.com
```

## 🔍 **Testing**

### **TDA Test Compatibility**
- **Button IDs**: Match React application exactly
- **Component Selectors**: Identical CSS classes and structure
- **Error Scenarios**: Same error handling and responses
- **Demo Features**: Identical functionality for automation

### **Manual Testing**
```bash
# Test Flask backend (default)
http://localhost:4200/

# Test all backends
http://localhost:4200/?backend=flask
http://localhost:4200/?backend=express
http://localhost:4200/?backend=springboot
http://localhost:4200/?backend=aspnetcore
http://localhost:4200/?backend=laravel
http://localhost:4200/?backend=rails

# Test SE tagging
http://localhost:4200/?se=wassim

# Test error scenarios
http://localhost:4200/?crash=true&errnum=1
```

## 📊 **Sentry Configuration**

### **Project Details**
- **Project**: `staging-angular`
- **Organization**: `team-se`
- **Environment**: `local`, `staging`, `production`

### **Features Enabled**
- ✅ **Error Monitoring**: Automatic error capture
- ✅ **Performance Tracking**: Page load metrics
- ✅ **Session Replay**: User interaction recording
- ✅ **Console Logging**: All logs sent to Sentry
- ✅ **SE Tagging**: Sales engineer identification
- ✅ **Backend Correlation**: Error context with backend type

## 🛠️ **Development**

### **Adding New Components**
```bash
ng generate component components/new-component
```

### **Adding New Services**
```bash
ng generate service services/new-service
```

### **Building and Testing**
```bash
# Build
npm run build

# Test
npm test

# Lint
npm run lint
```

## 🔗 **Related Projects**

- **React Frontend**: Reference implementation for TDA compatibility
- **Backend Services**: Flask, Express, Spring Boot, ASP.NET Core, Laravel, Ruby on Rails
- **TDA Tests**: Automated testing framework

## 📝 **Notes**

- **Backend Default**: Flask (same as React's Flask default)
- **Backend Support**: All 6 backends supported with dynamic switching
- **SE Tagging**: Supports `?se=wassim` for Sentry organization
- **Environment Handling**: Webpack integration with environment variable injection
- **Error Handling**: Intentional backend errors for demo purposes
- **TDA Compatibility**: Maintains exact match with React application

## 🆘 **Troubleshooting**

### **Common Issues**
1. **Backend not switching**: Check URL parameter `?backend=<backend_name>` (flask, express, springboot, aspnetcore, laravel, rails)
2. **Sentry not working**: Verify environment configuration and SENTRY_AUTH_TOKEN
3. **Build failures**: Check Node.js version matches `.nvmrc`

### **Getting Help**
- Check browser console for error messages
- Verify backend services are running
- Check Sentry dashboard for error reports

## 🔄 **Updates and Maintenance**

### **Adding New Backends**
1. **Update environment files**: Add new backend URLs
2. **Update config service**: Add backend switching logic
3. **Update deploy script**: Add backend configuration
4. **Test deployment**: Verify new backend works

### **Environment Changes**
1. **Update env-config**: Modify `env-config/{env}.env`
2. **Update webpack config**: Modify `webpack.config.js`
3. **Test deployment**: Verify changes work correctly
4. **Update documentation**: Keep this guide current

## 📝 **Best Practices**

1. **Always use deploy script** for consistent deployments
2. **Test backend switching** after each deployment
3. **Verify environment variables** are set correctly
4. **Use URL parameters** for runtime backend switching
5. **Maintain webpack configuration** for environment integration