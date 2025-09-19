import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { ProductsService, Product } from '../../services/products.service';
import { CartService } from '../../services/cart.service';
import { ThreeDotsComponent } from '../three-dots/three-dots.component';

/**
 * Products Component - Displays the main product catalog
 * 
 * This component shows all available products with:
 * - Product images, titles, descriptions, and prices
 * - Star ratings based on customer reviews
 * - "Add to cart" buttons for each product
 * - Loading animation while fetching products
 * 
 * Key Features:
 * - Fetches products from the backend API
 * - Handles adding products to the shopping cart
 * - Shows loading state with three-dots animation
 * - Displays star ratings for each product
 * 
 * TDA Test Compatibility:
 * - Button IDs match React app for automated testing
 * - Class names are consistent across frameworks
 */
@Component({
  selector: 'app-products',
  standalone: true,
  imports: [CommonModule, RouterModule, ThreeDotsComponent],
  templateUrl: './products.component.html',
  styleUrls: ['./products.component.css']
})
export class ProductsComponent implements OnInit {
  // Array to store all products from the API
  products: Product[] = [];
  
  // Flag to show/hide loading animation
  loading = true;
  
  // Flag to enable frontend slowdown demo mode (like React)
  frontendSlowdown = false;

  constructor(
    private productsService: ProductsService,
    private cartService: CartService,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Check URL for frontend slowdown parameter (like React)
    this.initializeFromUrl();
    
    // Load products when component initializes
    this.loadProducts();
  }

  /**
   * Initializes component from URL parameters
   * Mirrors React's URL parameter handling for demo features
   */
  private initializeFromUrl(): void {
    const urlParams = new URLSearchParams(window.location.search);
    const currentPath = window.location.pathname;
    
    // Enable slowdown mode if URL contains specific path or parameter
    this.frontendSlowdown = currentPath === '/products-fes' || urlParams.get('frontendSlowdown') === 'true';
  }

  /**
   * Fetches products from the backend API
   * Sets loading state and handles any errors
   * Limits products to first 4 to match React app behavior
   * Handles frontend slowdown mode for performance testing
   */
  loadProducts(): void {
    this.loading = true;
    
    this.productsService.getProducts(this.frontendSlowdown).subscribe({
      next: (products) => {
        // Handle products based on frontend slowdown mode (like React)
        if (this.frontendSlowdown) {
          // When triggering a frontend-only slowdown, cause a slow render problem
          // Create 150 products like React does for performance testing
          this.products = Array(150)
            .fill(products.slice(0, 4))
            .flat()
            .map((p, n) => {
              p.id = n;
              return p;
            });
        } else {
          // Limit to first 4 products to match React app behavior
          // This ensures TDA test compatibility and consistent UI
          this.products = products.slice(0, 4);
        }
        
        this.loading = false;
      },
      error: (error) => {
        console.error('❌ Error loading products:', error);
        console.error('❌ Error details:', {
          status: error.status,
          statusText: error.statusText,
          url: error.url,
          message: error.message
        });
        this.loading = false;
        // Set empty array to show "No products available" message
        this.products = [];
      }
    });
  }

  /**
   * Handles clicking on a product to view details
   * Navigates to the product detail page
   * 
   * @param event - The click event object
   * @param product - The product that was clicked
   */
  onProductClick(event: Event, product: Product): void {
    // Prevent the click from bubbling up to parent elements
    event.stopPropagation();
    
    // Navigate to the product detail page
    this.router.navigate(['/product', product.id]);
  }

  /**
   * Adds a product to the shopping cart
   * Prevents the click from triggering product navigation
   * 
   * @param event - The click event object
   * @param product - The product to add to cart
   */
  addToCart(event: Event, product: Product): void {
    // Stop the click event from bubbling up
    // This prevents the product click handler from running
    event.stopPropagation();
    
    // Add the product to the cart
    this.cartService.addProduct(product);
  }

  /**
   * Generates an array of star ratings for display
   * Hardcoded to match React exactly - no calculations needed
   * 
   * @param product - The product to generate stars for
   * @returns Array of HTML star symbols (filled or empty)
   */
  getStars(product: Product): string[] {
    // Hardcoded stars to match React exactly - no backend dependency
    // Product 1: 4.2 stars (4 filled, 1 empty)
    // Product 2: 3.8 stars (3 filled, 2 empty) 
    // Product 3: 4.5 stars (4 filled, 1 empty)
    // Product 4: 4.0 stars (4 filled, 1 empty)
    
    const hardcodedRatings = [4.2, 3.8, 4.5, 4.0];
    const productIndex = product.id - 1; // Convert to 0-based index
    const averageRating = hardcodedRatings[productIndex] || 4.0;
    
    // Generate 5 stars using HTML entities (exactly like React)
    const stars: string[] = [];
    for (let i = 1; i <= 5; i++) {
      if (i <= averageRating) {
        // Filled star (&#9733;) - same as React
        stars.push('&#9733;');
      } else {
        // Empty star (&#9734;) - same as React
        stars.push('&#9734;');
      }
    }
    
    return stars;
  }

  /**
   * Gets the hardcoded review count for each product
   * Matches React exactly - no backend dependency
   * 
   * @param product - The product to get review count for
   * @returns Hardcoded review count
   */
  getReviewCount(product: Product): number {
    // Hardcoded review counts to match React exactly
    // Product 1: 12 reviews
    // Product 2: 8 reviews  
    // Product 3: 15 reviews
    // Product 4: 10 reviews
    
    const hardcodedCounts = [12, 8, 15, 10];
    const productIndex = product.id - 1; // Convert to 0-based index
    return hardcodedCounts[productIndex] || 10;
  }

  /**
   * Track function for Angular's *ngFor directive
   * Helps Angular efficiently update the DOM when the products array changes
   * 
   * @param index - The index of the star in the array
   * @param star - The star HTML symbol
   * @returns A unique identifier for each star
   */
  trackByStar(index: number, star: string): string {
    return `${index}-${star}`;
  }
}