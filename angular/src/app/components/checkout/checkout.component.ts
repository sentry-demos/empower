import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CartService, CartState, CartItem } from '../../services/cart.service';
import { Product } from '../../services/products.service';
import { ConfigService, CheckoutForm } from '../../services/config.service';
import { ThreeDotsComponent } from '../three-dots/three-dots.component';
import { FeatureFlagsService } from '../../services/feature-flags.service';
import * as Sentry from '@sentry/angular';

/**
 * Checkout Component - Handles the final purchase process
 * 
 * This component manages the checkout form and submission process:
 * - Displays a pre-filled checkout form with user information
 * - Handles form validation and submission
 * - Integrates with Sentry for error monitoring
 * - Manages the checkout flow and error handling
 * 
 * Key Features:
 * - Pre-filled form data for demo purposes
 * - Form validation and error handling
 * - Sentry integration for monitoring
 * - Cart state management
 * 
 * TDA Test Compatibility:
 * - Form structure matches React app for automated testing
 * - Button classes and IDs are consistent across frameworks
 * - Form submission flow mirrors React implementation
 */
@Component({
  selector: 'app-checkout',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule, ThreeDotsComponent],
  templateUrl: './checkout.component.html',
  styleUrls: ['./checkout.component.css']
})
@Sentry.TraceClass({ name: "CheckoutComponent" })
export class CheckoutComponent implements OnInit {
  // Current cart state (items, quantities, total)
  cart: CartState = { items: [], quantities: {}, total: 0 };
  
  // Form data object for checkout information
  form: CheckoutForm = {
    email: '',
    subscribe: '',
    firstName: '',
    lastName: '',
    address: '',
    city: '',
    country: '',
    state: '',
    zipCode: ''
  };

  // Loading state for smooth checkout experience (like React)
  loading = false;

  constructor(
    private cartService: CartService,
    private configService: ConfigService,
    private router: Router,
    private featureFlagsService: FeatureFlagsService
  ) {}

  ngOnInit(): void {
    // Subscribe to cart updates and load form data when component initializes
    this.cartService.cart$.subscribe(cart => {
      this.cart = cart;
    });
    
    // Load pre-filled form data for demo purposes
    this.loadFormData();
  }

  /**
   * Loads pre-filled form data from the configuration service
   * This provides demo data so users don't have to type everything
   */
  loadFormData(): void {
    // Get pre-filled form values from the config service
    this.form = this.configService.getInitialFormValues();
  }

  /**
   * Handles form submission when user clicks "Complete order"
   * Processes the checkout and handles any errors
   * Mirrors React's checkout behavior for TDA compatibility
   * The checkout will intentionally fail to showcase Sentry error monitoring
   * 
   * @param event - The form submission event
   */
  @Sentry.TraceMethod({ name: "CheckoutComponent.onSubmit" })
  async onSubmit(event: Event): Promise<void> {
    // Prevent the default form submission behavior
    event.preventDefault();

    // Check if rage click mode is enabled (like React)
    if (this.configService.getRageclick()) {
      // Do nothing - after enough clicks, this will be detected as unusual behavior
      return;
    }

    // Scroll to top (like React)
    window.scrollTo({
      top: 0,
      behavior: 'auto'
    });

    // Set loading state for smooth experience (like React)
    this.loading = true;

    try {
      // Evaluate feature flags exactly as per Sentry documentation
      this.featureFlagsService.evaluateFeatureFlags();
      
      // Process the checkout (this will intentionally fail to showcase Sentry)
      await this.processCheckout();
      
      // If successful, navigate to complete page (like React)
      this.router.navigate(['/complete']);
    } catch (error) {
      // This is the expected behavior - checkout fails to showcase Sentry
      console.error('Checkout error (expected for demo):', error);
      
      // Capture the error in Sentry for monitoring (matches React exactly)
      Sentry.captureException(error);
      
      // Navigate to error page to show the error (like React)
      this.router.navigate(['/error']);
    } finally {
      // Always reset loading state
      this.loading = false;
    }
  }

  /**
   * Makes actual API call to backend like React does
   * The backend will intentionally fail to showcase Sentry error monitoring
   * 
   * @returns Promise<Response> - The checkout API response
   */
  @Sentry.TraceMethod({ name: "CheckoutComponent.processCheckout" })
  private async processCheckout(): Promise<Response> {
    
    const itemsInCart = this.cartService.getCartItemCount();

    // Get backend URL from config service (supports Laravel/Flask switching)
    const backendUrl = this.configService.getBackendUrl();
    const backendType = this.configService.getCurrentBackendType();
    const checkoutUrl = `${backendUrl}/checkout?v2=true`;
    

    const requestBody = {
      cart: this.cart,
      form: this.form,
      validate_inventory: this.configService.getCheckoutSuccess() ? "false" : "true"
    };


    try {
      const response = await fetch(checkoutUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      })
      .catch((error) => {
        // Handle fetch errors like React does - convert to response object
        return { ok: false, error: error, status: undefined, statusText: undefined };
      });

      if (!response.ok) {
        console.error("Checkout failed with status:", (response as any).status);
        
        if (!(response as any).error || (response as any).status === undefined) {
          const error = new Error(`${(response as any).status} - ${(response as any).statusText || 'Internal Server Error'}`);
          throw error;
        } else {
          // Handle network errors like React does
          if ((response as any).error instanceof TypeError && (response as any).error.message === "Failed to fetch") {
            throw new Error("Fetch promise rejected in Checkout due to either an actual network issue, malformed URL, etc or CORS headers not set on HTTP 500: " + (response as any).error);
          } else {
            throw new Error("Checkout request failed: " + (response as any).error);
          }
        }
      }

      return response as Response;
    } catch (error) {
      console.error("Checkout request failed:", error);
      throw error;
    }
  }

  /**
   * Gets the current quantity of a specific product in the cart
   * Returns 0 if the product is not in the cart
   * 
   * @param itemId - The ID of the product to get quantity for
   * @returns The current quantity (0 if not in cart)
   */
  getQuantity(itemId: number): number {
    return this.cart.quantities[itemId] || 0;
  }

}
