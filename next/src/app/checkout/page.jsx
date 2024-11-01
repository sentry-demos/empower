
import React from 'react';
import Link from 'next/link';
import { checkoutAction } from '@/lib/data';
import CheckoutForm from '@/src/ui/checkout/CheckoutForm';

export default async function Checkout() {

  return (
    <div className="checkout-container">
      <CheckoutForm checkoutAction={checkoutAction} />
      <Link href={{ pathname: '/cart' }} className="sentry-unmask">
        Back to cart
      </Link>
    </div>
  );
}

