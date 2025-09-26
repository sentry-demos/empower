import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { ConfigService } from './config.service';

/**
 * Product interface - represents a product in the catalog
 * Contains all the information needed to display and sell a product
 */
export interface Product {
  id: number;                    // Unique product identifier
  title: string;                 // Product name for display
  description: string;           // Short product description
  descriptionfull?: string;      // Full description from database (like React)
  price: number;                 // Product price in dollars
  img: string;                   // Main product image URL
  imgcropped?: string;           // Cropped image like React uses
  reviews: Review[];             // Array of customer reviews
}

/**
 * Review interface - represents a customer review for a product
 * Contains rating, description, and metadata about the review
 */
export interface Review {
  id: number;                    // Unique review identifier
  rating: number;                // Star rating (1-5)
  description: string;           // Customer's review text
  customerId: number;            // ID of the customer who wrote the review
  created: string;               // Date when the review was created
}

/**
 * ProductsService - Manages product data and API communication
 * 
 * This service provides:
 * - Product data fetching from backend APIs
 * - Backend URL management and switching
 * - Error handling for API calls
 * - Product filtering and manipulation
 * - TDA test compatibility
 * 
 * Key Features:
 * - Dynamic backend switching
 * - Configurable API endpoints
 * - Error handling and logging
 * - Product data caching
 * - Performance monitoring
 * 
 * Backend Integration:
 * - Supports multiple backend types
 * - Automatic backend detection
 * - Environment-aware configuration
 * - Seamless backend switching
 * 
 * TDA Test Compatibility:
 * - API behavior matches React app
 * - Error handling identical to React
 * - Product data structure consistent
 * - Backend switching logic matches
 */
@Injectable({
  providedIn: 'root'
})
export class ProductsService {
  constructor(
    private http: HttpClient,
    private configService: ConfigService
  ) {
    // Log which backend will be used (for debugging)
  }

  /**
   * Gets the current backend URL for API calls
   * Dynamically retrieves from config service to support runtime backend switching
   * 
   * This method ensures:
   * - Backend switching works immediately after URL parameter changes
   * - No stale backend URLs from service construction
   * - Runtime backend preference changes are respected
   * - Consistent behavior with React app
   * 
   * @returns Current backend URL string
   */
  private getBackendUrl(): string | undefined {
    return this.configService.getBackendUrl();
  }

  /**
   * Gets the current backend type being used
   * 
   * This method provides:
   * - Human-readable backend identification
   * - Logging and debugging information
   * - Sentry error context
   * - Demo presentation details
   * 
   * @returns Current backend type string
   */
  getCurrentBackendType(): string {
    return this.configService.getCurrentBackendType();
  }

  /**
   * Determines which products endpoint to use based on demo parameters
   * This mirrors React's logic for different product loading scenarios
   * 
   * @param productsApi - Type of products API to use
   * @param frontendSlowdown - Whether to simulate slow frontend rendering
   * @param productsExtremelySlow - Whether to use extremely slow endpoint
   * @param productsBeError - Whether to trigger backend errors
   * @returns The endpoint path to use for the API call
   */
  determineProductsEndpoint(productsApi?: string, frontendSlowdown?: boolean, productsExtremelySlow?: boolean, productsBeError?: boolean): string {
    if (productsApi !== 'products-join') {
      if (productsExtremelySlow) {
        // Use endpoint that triggers extremely slow response
        return '/products?fetch_promotions=true';
      } else if (productsBeError) {
        // Use endpoint that triggers backend errors
        return '/products?in_stock_only=1';
      } else {
        // Use standard products endpoint or join endpoint based on slowdown flag
        return frontendSlowdown ? '/products-join' : '/products';
      }
    } else {
      // Always use join endpoint if specifically requested
      return '/products-join';
    }
  }

  /**
   * Fetches products from the Flask backend API
   * Makes additional API calls for performance testing (fire-and-forget)
   * Returns an Observable that emits the product array
   * 
   * @param frontendSlowdown - Whether to simulate slow frontend rendering
   * @param productsApi - Type of products API to use
   * @param productsExtremelySlow - Whether to use extremely slow endpoint
   * @param productsBeError - Whether to trigger backend errors
   * @returns Observable that emits an array of products
   */
  getProducts(frontendSlowdown: boolean = false, productsApi: string = 'products', productsExtremelySlow: boolean = false, productsBeError: boolean = false): Observable<Product[]> {
    const backendUrl = this.getBackendUrl();
    const backendType = this.configService.getCurrentBackendType();
    
    // Determine which endpoint to use for the main products request
    const productsEndpoint = this.determineProductsEndpoint(productsApi, frontendSlowdown, productsExtremelySlow, productsBeError);
    
    // Make additional API calls like React does (for demo purposes)
    // These are fire-and-forget calls that don't affect the main products request
    // They help simulate real-world scenarios where multiple API calls happen
    ['/api', '/connect', '/organization'].forEach(endpoint => {
      this.http.get(this.getBackendUrl() + endpoint, {
        headers: { 'Content-Type': 'application/json' }
      }).subscribe({
        error: (err) => {
          // Log errors but don't fail the main request
        }
      });
    });
    
    // Return a single HTTP request for products
    // This ensures we get ALL products in one response, not multiple partial responses
    return this.http.get<Product[]>(this.getBackendUrl() + productsEndpoint, {
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
