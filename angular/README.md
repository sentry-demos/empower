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

### **Development Workflow**
- **`npm start`**: UI development with localhost backends (start backends separately if needed)
- **`./deploy.sh angular flask --env=local`**: Full integration testing with local Flask backend
- **`./deploy.sh angular --env=staging`**: Production-like testing with staging backends

### **Using Deploy Script (Recommended)**
```bash
# Deploy Angular with Flask backend (default)
./deploy.sh angular --env=local

# Deploy Angular with Laravel backend
./deploy.sh angular laravel --env=local

# Deploy to staging
./deploy.sh angular --env=staging

# Deploy to production
./deploy.sh angular --env=production
```

## 🌐 **Backend Configuration**

### **Default Backend: Flask**
- **Local**: `http://localhost:8080`
- **Staging**: `https://staging-flask.empower-plant.com`

### **Alternative Backend: Laravel**
- **Local**: `http://localhost:8000`
- **Staging**: `https://staging-laravel.empower-plant.com`

### **Backend Switching**
The application supports dynamic backend switching via URL parameters:

```bash
# Use Flask (default)
http://localhost:4200/

# Switch to Laravel
http://localhost:4200/?backend=laravel

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
- **Multiple Backends**: Support for Laravel, Flask, and more
- **Dynamic Switching**: Runtime backend selection
- **Environment Aware**: Automatic configuration per environment
- **Deploy Script Integration**: Seamless deployment workflow

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
1. **Specified Backends**: If `./deploy.sh angular laravel` is used, Laravel backend is configured
2. **Default Backend**: Flask is always set as default backend
3. **Runtime Switching**: Users can switch between available backends via URL parameters

### **Environment Variables**

The deploy script automatically sets these environment variables:

#### **Local Environment**
```bash
ANGULAR_APP_FLASK_BACKEND=http://localhost:8080
ANGULAR_APP_LARAVEL_BACKEND=http://localhost:8000
```

#### **Staging Environment**
```bash
ANGULAR_APP_FLASK_BACKEND=https://staging-flask.empower-plant.com
ANGULAR_APP_LARAVEL_BACKEND=https://staging-laravel.empower-plant.com
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

# Test Laravel backend
http://localhost:4200/?backend=laravel

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
- **Laravel Backend**: Default backend service
- **Flask Backend**: Alternative backend service
- **TDA Tests**: Automated testing framework

## 📝 **Notes**

- **Backend Default**: Flask (same as React's Flask default)
- **SE Tagging**: Supports `?se=wassim` for Sentry organization
- **Environment Handling**: Uses hardcoded values with webpack integration ready
- **Error Handling**: Intentional backend errors for demo purposes
- **TDA Compatibility**: Maintains exact match with React application

## 🆘 **Troubleshooting**

### **Common Issues**
1. **Backend not switching**: Check URL parameter `?backend=laravel`
2. **Sentry not working**: Verify environment configuration
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