import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import { Product } from './products.service';

/**
 * CartItem interface - represents a single item in the shopping cart
 * Contains essential product information needed for cart display
 */
export interface CartItem {
  id: number;        // Unique product identifier
  title: string;     // Product name for display
  img: string;       // Product image URL
  price: number;     // Product price in dollars
}

/**
 * CartState interface - represents the complete state of the shopping cart
 * Contains all items, quantities, and calculated totals
 */
export interface CartState {
  items: Product[];                    // Array of unique products in cart
  quantities: { [key: number]: number }; // Map of product ID to quantity
  total: number;                        // Total cost of all items in cart
}

/**
 * CartService - Manages shopping cart state and persistence
 * 
 * This service provides:
 * - Shopping cart state management
 * - Product addition and removal
 * - Cart persistence in session storage
 * - Cart total calculations
 * - TDA test compatibility
 * 
 * Key Features:
 * - Reactive cart state with BehaviorSubject
 * - Session storage persistence
 * - Immutable state updates
 * - Cart item management
 * - Total calculation
 * 
 * State Management:
 * - Uses RxJS BehaviorSubject for reactive updates
 * - Immutable state updates for performance
 * - Automatic persistence to session storage
 * - Real-time cart updates across components
 * 
 * TDA Test Compatibility:
 * - Cart behavior matches React app exactly
 * - Same state management patterns
 * - Identical persistence logic
 * - Consistent API interface
 */
@Injectable({
  providedIn: 'root'
})
export class CartService {
  // Cart state observable - emits cart updates to all subscribers
  private cartSubject = new BehaviorSubject<CartState>({
    items: [],
    quantities: {},
    total: 0
  });

  // Public observable for components to subscribe to cart changes
  public cart$ = this.cartSubject.asObservable();

  constructor() {
    // Load cart from session storage on service initialization
    this.loadCartFromStorage();
  }

  /**
   * Gets the current cart state
   * 
   * This method provides:
   * - Current cart items and quantities
   * - Real-time cart state access
   * - Synchronous cart data retrieval
   * - Component state synchronization
   * 
   * @returns Current CartState object
   */
  getCart(): CartState {
    return this.cartSubject.value;
  }

  /**
   * Adds a product to the cart
   * 
   * This method:
   * - Adds product to cart items array
   * - Increments quantity if product already exists
   * - Updates cart total automatically
   * - Persists changes to session storage
   * - Emits cart update to all subscribers
   * 
   * @param product - The product to add to cart
   */
  addProduct(product: Product): void {
    
    // Get current cart state and create a new copy (immutable update)
    const currentCart = this.cartSubject.value;
    const existingItemIndex = currentCart.items.findIndex(item => item.id === product.id);
    
    let newCart: CartState;
    
    if (existingItemIndex >= 0) {
      // Product already exists - increment quantity
      const updatedItems = [...currentCart.items];
      const updatedQuantities = { ...currentCart.quantities };
      
      updatedQuantities[product.id] = (updatedQuantities[product.id] || 0) + 1;
      
      newCart = {
        ...currentCart,
        quantities: updatedQuantities,
        total: this.calculateTotal(updatedItems, updatedQuantities)
      };
    } else {
      // New product - add to cart
      const newItems = [...currentCart.items, product];
      const newQuantities = { ...currentCart.quantities, [product.id]: 1 };
      
      newCart = {
        items: newItems,
        quantities: newQuantities,
        total: this.calculateTotal(newItems, newQuantities)
      };
    }
    
    // Emit the new cart state to all subscribers
    this.cartSubject.next(newCart);
    
    // Save the updated cart to session storage
    this.saveCartToStorage(newCart);
  }

  /**
   * Removes a product from the cart
   * 
   * This method:
   * - Removes product from cart items array
   * - Decrements quantity if multiple exist
   * - Updates cart total automatically
   * - Persists changes to session storage
   * - Emits cart update to all subscribers
   * 
   * @param product - The product to remove from cart
   */
  removeProduct(product: Product): void {
    const currentCart = this.cartSubject.value;
    const currentQuantity = currentCart.quantities[product.id] || 0;
    
    if (currentQuantity <= 1) {
      // Remove product completely if quantity is 1 or less
      const newItems = currentCart.items.filter(item => item.id !== product.id);
      const newQuantities = { ...currentCart.quantities };
      delete newQuantities[product.id];
      
      const newCart: CartState = {
        items: newItems,
        quantities: newQuantities,
        total: this.calculateTotal(newItems, newQuantities)
      };
      
      this.cartSubject.next(newCart);
      this.saveCartToStorage(newCart);
    } else {
      // Decrement quantity if more than 1
      const newQuantities = { ...currentCart.quantities };
      newQuantities[product.id] = currentQuantity - 1;
      
      const newCart: CartState = {
        ...currentCart,
        quantities: newQuantities,
        total: this.calculateTotal(currentCart.items, newQuantities)
      };
      
      this.cartSubject.next(newCart);
      this.saveCartToStorage(newCart);
    }
  }

  /**
   * Adds a cart item to the cart (helper method for CartItem type)
   * 
   * This method converts CartItem to Product format and adds to cart.
   * Used by components that work with CartItem objects.
   * 
   * @param cartItem - The cart item to add
   */
  addCartItem(cartItem: CartItem): void {
    // Convert CartItem to Product format
    const product: Product = {
      id: cartItem.id,
      title: cartItem.title,
      price: cartItem.price,
      description: '', // Default empty description
      img: cartItem.img, // Use 'img' from CartItem
      reviews: [] // Default empty reviews array
    };
    
    this.addProduct(product);
  }

  /**
   * Removes a cart item from the cart (helper method for CartItem type)
   * 
   * This method converts CartItem to Product format and removes from cart.
   * Used by components that work with CartItem objects.
   * 
   * @param cartItem - The cart item to remove
   */
  removeCartItem(cartItem: CartItem): void {
    // Convert CartItem to Product format
    const product: Product = {
      id: cartItem.id,
      title: cartItem.title,
      price: cartItem.price,
      description: '', // Default empty description
      img: cartItem.img, // Use 'img' from CartItem
      reviews: [] // Default empty reviews array
    };
    
    this.removeProduct(product);
  }

  /**
   * Clears the entire cart
   * 
   * This method:
   * - Removes all items from cart
   * - Resets quantities to empty object
   * - Sets total to 0
   * - Persists empty cart to session storage
   * - Emits cart update to all subscribers
   */
  clearCart(): void {
    const emptyCart: CartState = {
      items: [],
      quantities: {},
      total: 0
    };
    
    this.cartSubject.next(emptyCart);
    this.saveCartToStorage(emptyCart);
  }

  /**
   * Gets the total number of items in the cart
   * Counts all quantities across all products
   * 
   * This method is useful for:
   * - Displaying cart item count in UI
   * - Cart badge notifications
   * - Cart summary information
   * - TDA test verification
   * 
   * @returns Total number of items (sum of all quantities)
   */
  getCartItemCount(): number {
    const cart = this.cartSubject.value;
    if (!cart || !cart.quantities) {
      return 0;
    }
    
    // Sum up all quantities across all products
    return Object.values(cart.quantities).reduce((sum, quantity) => sum + quantity, 0);
  }

  /**
   * Gets the total price of all items in the cart
   * 
   * This method provides:
   * - Current cart total for display
   * - Checkout total calculation
   * - Cart summary information
   * - TDA test verification
   * 
   * @returns Total price in dollars
   */
  getCartTotal(): number {
    return this.cartSubject.value.total;
  }

  /**
   * Resets the cart to empty state (alias for clearCart)
   * 
   * This method:
   * - Removes all items from cart
   * - Resets quantities to empty object
   * - Sets total to 0
   * - Persists empty cart to session storage
   * - Emits cart update to all subscribers
   * 
   * Note: This is an alias for clearCart() to maintain compatibility
   */
  resetCart(): void {
    this.clearCart();
  }

  /**
   * Calculates the total price of all items in the cart
   * 
   * This method:
   * - Iterates through cart items
   * - Multiplies price by quantity for each item
   * - Sums all item totals
   * - Returns the final cart total
   * 
   * @param items - Array of cart items
   * @param quantities - Object mapping product IDs to quantities
   * @returns Total price as number
   */
  private calculateTotal(items: Product[], quantities: { [key: number]: number }): number {
    return items.reduce((total, item) => {
      const quantity = quantities[item.id] || 0;
      return total + (item.price * quantity);
    }, 0);
  }

  /**
   * Saves cart state to session storage
   * 
   * This method:
   * - Converts cart state to JSON string
   * - Stores in session storage with key 'empower-plant-cart'
   * - Enables cart persistence across page reloads
   * - Maintains cart state during browser session
   * 
   * @param cart - The cart state to save
   */
  private saveCartToStorage(cart: CartState): void {
    sessionStorage.setItem('empower-plant-cart', JSON.stringify(cart));
  }

  /**
   * Loads cart state from session storage
   * 
   * This method:
   * - Retrieves cart data from session storage
   * - Parses JSON string back to CartState object
   * - Emits loaded cart state to subscribers
   * - Restores cart state on page reload
   */
  private loadCartFromStorage(): void {
    const savedCart = sessionStorage.getItem('empower-plant-cart');
    
    if (savedCart) {
      try {
        const cart: CartState = JSON.parse(savedCart);
        this.cartSubject.next(cart);
      } catch (error) {
        console.error('Failed to parse saved cart:', error);
        // If parsing fails, start with empty cart
        this.cartSubject.next({
          items: [],
          quantities: {},
          total: 0
        });
      }
    }
  }
}
