import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { CartService, CartState } from '../../services/cart.service';
import * as Sentry from '@sentry/angular';

@Component({
  selector: 'app-complete',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './complete.component.html',
  styleUrls: ['./complete.component.css']
})
export class CompleteComponent implements OnInit {
  orderedCart: CartState = { items: [], quantities: {}, total: 0 };
  orderNumber: number = 0;

  constructor(private cartService: CartService) {}

  ngOnInit() {
    // Get current cart state
    this.cartService.cart$.subscribe(cart => {
      this.orderedCart = cart;
    });

    // Generate random order number (like React)
    this.orderNumber = Math.floor(Math.random() * 99999) + 10000;

    // Reset cart after successful checkout (like React)
    this.cartService.resetCart();

    // Handle replay flush exactly like React
    window.setTimeout(() => {
      const replay = Sentry.getReplay();
      if (replay) {
        replay.flush();
      }
    }, 1000);
  }
}
