import React from 'react';

import { Suspense } from 'react';

import '/src/styles/index.css';
import '/src/styles/footer.css';
import '/src/styles/nav.css';
import '/src/styles/products.css';
import '/src/styles/about.css';
import '/src/styles/cart.css';
import '/src/styles/checkout.css';
import '/src/styles/complete.css';
import '/src/styles/product.css';

import SentryQueryInitializer from '/src/ui/SentryQueryInitializer';
import HomeContent from '/src/ui/HomeContent';

export default function RootLayout({
  // Layouts must accept a children prop.
  // This will be populated with nested layouts or pages
  children,
}) {
  return (
    <html lang="en">
      <body>
        <Suspense>
          <SentryQueryInitializer />
        </Suspense>
        <Suspense>
          <HomeContent>{children}</HomeContent>
        </Suspense>
      </body>
    </html>
  );
}
