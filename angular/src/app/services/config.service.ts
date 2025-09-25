import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';

/**
 * CheckoutForm interface - represents the checkout form data
 * Contains all the fields needed for customer checkout information
 */
export interface CheckoutForm {
  email: string;        // Customer's email address
  subscribe: string;    // Newsletter subscription preference
  firstName: string;    // Customer's first name
  lastName: string;     // Customer's last name
  address: string;      // Customer's street address
  city: string;         // Customer's city
  country: string;      // Customer's country
  state: string;        // Customer's state/province
  zipCode: string;      // Customer's postal/zip code
}

/**
 * ConfigService - Manages application configuration and demo parameters
 * 
 * This service provides:
 * - URL parameter handling for demo features
 * - Configuration for different demo scenarios
 * - Backend URL management with dynamic switching
 * - Form data initialization
 * - SE tag management for Sentry
 * 
 * Key Features:
 * - Reads URL parameters on initialization
 * - Manages session storage for demo state
 * - Provides pre-filled form data for demos
 * - Supports different checkout scenarios
 * - Dynamic backend switching
 * 
 * TDA Test Compatibility:
 * - Configuration behavior matches React app for automated testing
 * - URL parameter handling follows similar patterns
 * - Form data structure is consistent across frameworks
 * - Backend switching logic identical to React
 * 
 * Backend Switching:
 * - Default: Flask backend
 */
@Injectable({
  providedIn: 'root'
})
export class ConfigService {
  // Sales Engineer identifier from URL parameters
  private se: string | null = null;
  
  // Flag to enable rage click detection demo
  private rageclick: boolean = false;
  
  // Flag to enable successful checkout demo
  private checkoutSuccess: boolean = false;
  
  // Flag to enable error boundary demo
  private errorBoundary: boolean = false;

  constructor() {
    // Initialize configuration from URL parameters when service starts
    this.initializeFromUrl();
  }

  /**
   * Reads URL parameters and initializes service configuration
   * Sets up demo flags and sales engineer identification
   * 
   * This method is called during service initialization and:
   * - Extracts 'se' parameter for Sentry tagging
   * - Sets up demo mode flags
   * - Stores configuration in session storage for persistence
   * - Handles both URL parameters and session storage fallback
   */
  private initializeFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    
    // Handle 'backend' parameter (like React)
    // This determines which backend to use for all API calls
    const backendParam = urlParams.get('backend');
    if (backendParam === 'laravel') {
      sessionStorage.setItem('backend', 'laravel');
    } else {
      sessionStorage.setItem('backend', 'flask');
    }
    
    // Handle 'se' parameter (session storage)
    // This identifies which sales engineer is running the demo
    this.se = urlParams.get('se');
    if (this.se) {
      // Store in session storage for persistence across page reloads
      sessionStorage.setItem('se', this.se);
    } else {
      // Try to get from session storage if not in URL
      this.se = sessionStorage.getItem('se');
    }

    // Handle 'rageclick' parameter
    // Enables demo mode for detecting unusual user behavior
    this.rageclick = urlParams.get('rageclick') === 'true';

    // Handle 'cexp' parameter for checkout success
    // Allows demo of successful checkout flow
    const cexp = urlParams.get('cexp');
    if (cexp === 'checkout_success') {
      this.checkoutSuccess = true;
    }

    // Handle 'error_boundary' parameter
    // Enables demo of error boundary functionality
    this.errorBoundary = urlParams.get('error_boundary') === 'true';
  }

  /**
   * Gets initial form values based on 'se' parameter (like React)
   * Provides different form data for TDA tests vs. regular demos
   * 
   * TDA Test Sessions:
   * - Detected by regex pattern: /[^-]+-tda-[^-]+-/
   * - Return empty form for realistic-looking demos
   * - Used by automated testing frameworks
   * 
   * Regular Demo Sessions:
   * - Return pre-filled form data for easy demo presentation
   * - Makes checkout flow demonstration smoother
   * - Consistent with React app behavior
   * 
   * @returns CheckoutForm object with pre-filled or empty data
   */
  getInitialFormValues(): CheckoutForm {
    const se = sessionStorage.getItem('se');
    
    // Regular expression to detect TDA test sessions
    // TDA sessions have a specific naming pattern
    const seTdaPrefixRegex = /[^-]+-tda-[^-]+-/;
    
    if (se && seTdaPrefixRegex.test(se)) {
      // Empty form for TDA (realistic-looking Replay)
      // This makes the demo look more realistic for automated testing
      return {
        email: '',
        subscribe: '',
        firstName: '',
        lastName: '',
        address: '',
        city: '',
        country: '',
        state: '',
        zipCode: '',
      };
    } else {
      // Pre-filled form for demos (like React)
      // This makes it easier for demo presenters to show the checkout flow
      return {
        email: 'plant.lover@example.com',
        subscribe: '',
        firstName: 'Jane',
        lastName: 'Greenthumb',
        address: '123 Main Street',
        city: 'San Francisco',
        country: 'United States of America',
        state: 'CA',
        zipCode: '94122',
      };
    }
  }

  /**
   * Gets the backend URL for API calls
   * Uses stored backend preference from session storage (like React)
   * 
   * URL Examples:
   * - / → Uses Flask backend (default)
   * - /?backend=laravel → Uses Laravel backend
   * - /?backend=laravel&se=wassim → Uses Laravel + SE tagging
   * 
   * @returns Backend URL string for API calls
   */
  getBackendUrl(): string {
    const backendPreference = sessionStorage.getItem('backend') || 'flask';
    
    if (backendPreference === 'laravel') {
      return environment.BACKEND_URL_LARAVEL;
    }
    
    // Default to Flask backend (Angular default, same as React's Flask default)
    return environment.BACKEND_URL_FLASK;
  }

  getCurrentBackendType(): string {
    const backendPreference = sessionStorage.getItem('backend') || 'flask';
    
    return backendPreference === 'laravel' ? 'laravel' : 'flask';
  }

  getSe(): string | null {
    return this.se;
  }

  getRageclick(): boolean {
    return this.rageclick;
  }

  getCheckoutSuccess(): boolean {
    return this.checkoutSuccess;
  }

  getErrorBoundary(): boolean {
    return this.errorBoundary;
  }
}
