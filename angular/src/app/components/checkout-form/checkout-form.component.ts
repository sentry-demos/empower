import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CartService, CartState } from '../../services/cart.service';
import { ConfigService, CheckoutForm } from '../../services/config.service';
import { ThreeDotsComponent } from '../three-dots/three-dots.component';
import { FeatureFlagsService } from '../../services/feature-flags.service';
import { measureRequestDuration } from '../../utils/measure-request-duration';
import { getTag } from '../../utils/sentry-utils';
import { environment } from '../../../environments/environment';
import * as Sentry from '@sentry/angular';
import { metrics } from '@sentry/browser';

@Component({
  selector: 'app-checkout-form',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule, ThreeDotsComponent],
  templateUrl: './checkout-form.component.html',
  styleUrls: ['./checkout-form.component.css']
})
@Sentry.TraceClass({ name: "CheckoutFormComponent" })
export class CheckoutFormComponent implements OnInit {
  cart: CartState = { items: [], quantities: {}, total: 0 };

  form: CheckoutForm = {
    email: '',
    subscribe: '',
    firstName: '',
    lastName: '',
    address: '',
    city: '',
    country: '',
    state: '',
    zipCode: '',
    promoCode: '',
  };

  loading = false;
  promoMessage = '';
  promoLoading = false;

  constructor(
    private cartService: CartService,
    private configService: ConfigService,
    private router: Router,
    private featureFlagsService: FeatureFlagsService
  ) {}

  ngOnInit(): void {
    this.cartService.cart$.subscribe(cart => {
      this.cart = cart;
    });
    this.loadFormData();
  }

  loadFormData(): void {
    this.form = this.configService.getInitialFormValues();
  }

  async handleApplyPromoCode(event: Event): Promise<void> {
    Sentry.startSpan({
      op: 'function',
      name: 'handleApplyPromoCode',
    }, async () => {
      event.preventDefault();

      console.info(`applying promo code '${this.form.promoCode}'...`);

      if (!this.form.promoCode.trim()) {
        this.promoMessage = 'Please enter a promo code';
        return;
      }

      this.promoLoading = true;
      this.promoMessage = '';

      try {
        const flaskBackend = environment.BACKEND_URL_FLASK;
        const response = await fetch(flaskBackend + '/apply-promo-code', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ value: this.form.promoCode.trim() }),
        });

        if (response.ok) {
          this.promoMessage = 'Promo successfully applied!';
        } else {
          const responseBody = await response.json();
          console.error(`failed to apply promo code: HTTP ${response.status} | body: `, responseBody);
          this.promoMessage = 'Unknown error applying promo code';
        }
      } catch (error) {
        console.error('Error applying promo code:', error);
        this.promoMessage = 'Unknown error when applying promo';
      } finally {
        this.promoLoading = false;
      }
    });
  }

  async onSubmit(event: Event): Promise<void> {
    event.preventDefault();

    if (this.configService.getRageclick()) {
      return;
    }

    await Sentry.startSpan(
      {
        name: 'checkout_submit',
        forceTransaction: true,
      },
      async (span) => {
        window.scrollTo({ top: 0, behavior: 'auto' });
        this.loading = true;
        let hadError = false;

        try {
          this.featureFlagsService.evaluateFeatureFlags();
          await this.checkout(this.cart, span);
        } catch (error) {
          Sentry.captureException(error);
          hadError = true;
        }

        this.loading = false;

        if (hadError) {
          this.router.navigate(['/error']);
        } else {
          this.router.navigate(['/complete']);
        }
      }
    );
  }

  private async checkout(cart: CartState, checkout_span: Sentry.Span): Promise<Response | { ok: boolean; error?: any; status?: number; statusText?: string }> {
    const itemsInCart = this.cartService.getCartItemCount();

    checkout_span.setAttribute('checkout_submit.click', 1);
    checkout_span.setAttribute('checkout_submit.num_items', itemsInCart);
    checkout_span.setAttribute('checkout_submit.order_total', cart.total);

    const tags: Record<string, any> = {
      'backendType': getTag('backendType'),
      'cexp': getTag('cexp'),
      'checkout_submit.num_items': itemsInCart,
      'checkout_submit.click': 1,
    };
    checkout_span.setAttributes(tags);

    metrics.count('checkout_submit.click', 1);
    metrics.distribution('checkout_submit.num_items', itemsInCart);
    metrics.distribution('checkout_submit.order_total', cart.total);

    return await Sentry.startSpan(
      {
        name: 'processCheckout',
        op: 'function',
      },
      async (span) => {
        const stopMeasurement = measureRequestDuration('/checkout');

        const backendUrl = this.configService.getBackendUrl();

        const response = await fetch(backendUrl + '/checkout?v2=true', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            cart: cart,
            form: this.form,
            validate_inventory: this.configService.getCheckoutSuccess() ? 'false' : 'true',
          }),
        })
        .catch((error) => {
          return { ok: false, error: error } as any;
        })
        .then((res: any) => {
          stopMeasurement();
          return res;
        });

        if (!response.ok) {
          span?.setAttribute('checkout_submit.error', 1);
          metrics.count('checkout_submit.error', 1);

          if (!response.error || response.status === undefined) {
            span?.setAttribute('status', response.status);
            metrics.distribution('checkout_submit.status', response.status);
            throw new Error([response.status, response.statusText || ' Internal Server Error'].join(' -'));
          } else {
            span?.setAttribute('status', 'unknown_error');
            if (response.error instanceof TypeError && response.error.message === 'Failed to fetch') {
              Sentry.captureException(new Error('Fetch promise rejected in Checkout due to either an actual network issue, malformed URL, etc or CORS headers not set on HTTP 500: ' + response.error));
            } else {
              Sentry.captureException(new Error('Checkout request failed: ' + response.error));
            }
          }
        } else {
          span?.setAttribute('checkout_submit.success', 1);
          metrics.count('checkout_submit.success', 1);
        }

        return response;
      }
    );
  }

  getQuantity(itemId: number): number {
    return this.cart.quantities[itemId] || 0;
  }

  isPromoSuccess(): boolean {
    return this.promoMessage.includes('successfully');
  }
}
