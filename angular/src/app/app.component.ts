import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, RouterOutlet } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CartService } from './services/cart.service';
import { ConfigService } from './services/config.service';
import { crasher } from './utils/errors';
import * as Sentry from '@sentry/angular';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule, Sentry.TraceModule],
  template: `
    <!-- Navigation -->
    <nav id="top-nav" class="show-mobile">
      <div class="nav-contents">
              <a routerLink="/home" href="/" id="home-link">
        <img src="./assets/empowerplant-logo.svg" class="logo" alt="logo" />
      </a>
        <div id="top-right-links">
          <a routerLink="/about" href="/about">About</a>
          <a routerLink="/products" href="/products">Products</a>
          <a routerLink="/cart" href="/cart">
            Cart
            <span *ngIf="cartHasItems">
              <span> ($</span>
              <span>{{ cartTotal }}.00</span>
              <span>)</span>
            </span>
          </a>
        </div>
      </div>
    </nav>

    <nav id="top-nav" class="show-desktop">
      <div class="nav-contents">
              <a routerLink="/home" href="/" id="home-link">
        <img src="./assets/empowerplant-logo.svg" class="logo" alt="logo" />
        Empower Plant
      </a>
        <div id="top-right-links">
          <a routerLink="/about" href="/about">About</a>
          <a routerLink="/products" href="/products">Products</a>
          <a routerLink="/cart" href="/cart">
            Cart
            <span *ngIf="cartHasItems">
              <span> ($</span>
              <span>{{ cartTotal }}.00</span>
              <span>)</span>
            </span>
          </a>
        </div>
      </div>
    </nav>

    <!-- Main Content Area -->
    <div id="body-container">
      <router-outlet></router-outlet>
    </div>

    <!-- Footer -->
    <footer id="footer">
      <div>
        <h2 class="h3">Sign up for plant tech news</h2>
        <div class="formContainer">
          <form (ngSubmit)="onEmailSubmit($event)">
            <label for="email-subscribe">Email</label>
            <input
              type="email"
              name="email-subscribe"
              id="email-subscribe"
              [(ngModel)]="email"
            />
            <button
              type="submit"
              class="subscribe-button"
            >
              Subscribe
            </button>
          </form>
          <p *ngIf="subscribed">{{ getSubscribedMessage() }}</p>
        </div>
        <p>
          © 2021 • Empower Plant • <a routerLink="/about" href="/about">About us</a>
        </p>
      </div>
    </footer>
  `,
  styles: []
})
export class AppComponent implements OnInit, OnDestroy {
  cartTotal: number = 0;
  cartHasItems: boolean = false;
  email: string = '';
  subscribed: boolean = false;
  private subscription: any = null;

  constructor(
    private cartService: CartService,
    private configService: ConfigService
  ) {
    
    // Check for crash parameter and trigger errors if needed (like React)
    // Call in constructor like React does, before component initialization
    crasher();
  }

  ngOnInit() {
    // Subscribe to cart changes to update the cart indicator
    this.subscription = this.cartService.cart$.subscribe(cart => {
      this.cartTotal = cart.total;
      this.cartHasItems = cart.items.length > 0;
    });
    
    // Also get initial cart state immediately
    const currentCart = this.cartService.getCart();
    this.cartTotal = currentCart.total;
    this.cartHasItems = currentCart.items.length > 0;
  }

  ngOnDestroy() {
    if (this.subscription) {
      this.subscription.unsubscribe();
    }
  }

  // Handle email subscription form submission
  onEmailSubmit(event: Event) {
    event.preventDefault();
    this.subscribed = true;
    // Send email subscription to queue (like React)
    this.sendToQueue();
  }

  /**
   * Sends email subscription to backend queue
   * Uses config service for backend URL (supports Laravel/Flask switching)
   */
  async sendToQueue() {
    try {
      const backendUrl = this.configService.getBackendUrl();
      const backendType = this.configService.getCurrentBackendType();
      
      
      const resp = await fetch(`${backendUrl}/enqueue`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'demo@example.com' })
      });

      if (resp.ok) {
        const data = await resp.json();
      }
    } catch (error) {
      console.error('Failed to send email subscription:', error);
    }
  }

  // Get subscription message
  getSubscribedMessage() {
    return 'You have successfully subscribed!';
  }
}
