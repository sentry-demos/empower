import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { CartService, CartState, CartItem } from '../../services/cart.service';
import { getTag } from '../../utils/sentry-utils';
import * as Sentry from '@sentry/angular';
import { metrics } from '@sentry/browser';

@Component({
  selector: 'app-cart',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './cart.component.html',
  styleUrls: ['./cart.component.css']
})
export class CartComponent implements OnInit {
  cart: CartState = { items: [], quantities: {}, total: 0 };

  constructor(private cartService: CartService) {}

  ngOnInit(): void {
    this.cartService.cart$.subscribe(cart => {
      this.cart = cart;
      this.emitCartMetrics();
    });
  }

  private emitCartMetrics(): void {
    const itemsInCart = this.cartService.getCartItemCount();
    const tags: Record<string, any> = {
      'backendType': getTag('backendType'),
      'cexp': getTag('cexp'),
      'items_in_cart': itemsInCart,
    };
    const span = Sentry.startInactiveSpan({ name: 'items_added_to_cart', op: 'function' });
    span.setAttributes(tags);
    span.end();
    metrics.distribution('items_in_cart', itemsInCart);
  }

  addProduct(item: CartItem): void {
    this.cartService.addCartItem(item);
  }

  removeProduct(item: CartItem): void {
    this.cartService.removeCartItem(item);
  }

  getQuantity(itemId: number): number {
    return this.cart.quantities[itemId] || 0;
  }

  getItemTotal(item: CartItem): number {
    const quantity = this.cart.quantities[item.id] || 0;
    return item.price * quantity;
  }
}
