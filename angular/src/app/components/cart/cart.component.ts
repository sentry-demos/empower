import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { CartService, CartState, CartItem } from '../../services/cart.service';

/**
 * Cart Component - Manages the shopping cart functionality
 * 
 * This component displays all items in the user's cart and provides:
 * - List of cart items with images, titles, and prices
 * - Quantity adjustment controls (+ and - buttons)
 * - Total price calculation
 * - Navigation to checkout
 * - Remove items functionality
 * 
 * Key Features:
 * - Real-time cart updates using CartService
 * - Quantity management for each product
 * - Price calculations including quantity multipliers
 * - Responsive design for mobile and desktop
 * 
 * TDA Test Compatibility:
 * - Button classes match React app for automated testing
 * - Navigation links use consistent patterns
 * - Cart item structure mirrors React implementation
 */
@Component({
  selector: 'app-cart',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './cart.component.html',
  styleUrls: ['./cart.component.css']
})
export class CartComponent implements OnInit {
  // Cart state object containing items, quantities, and total
  cart: CartState = { items: [], quantities: {}, total: 0 };

  constructor(private cartService: CartService) {}

  ngOnInit(): void {
    // Subscribe to cart updates when component initializes
    this.cartService.cart$.subscribe(cart => {
      this.cart = cart;
    });
  }

  /**
   * Adds one more of the specified product to the cart
   * Increases the quantity by 1
   * 
   * @param item - The cart item to add more of
   */
  addProduct(item: CartItem): void {
    this.cartService.addCartItem(item);
  }

  /**
   * Removes one of the specified product from the cart
   * Decreases the quantity by 1, removes completely if quantity becomes 0
   * 
   * @param item - The cart item to remove one of
   */
  removeProduct(item: CartItem): void {
    this.cartService.removeCartItem(item);
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

  /**
   * Calculates the total price for a specific cart item
   * Multiplies the item price by its quantity
   * 
   * @param item - The cart item to calculate total for
   * @returns The total price for this item (price × quantity)
   */
  getItemTotal(item: CartItem): number {
    const quantity = this.cart.quantities[item.id] || 0;
    return item.price * quantity;
  }
}
