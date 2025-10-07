import React from 'react';

import { Suspense } from 'react';

import SentryQueryInitializer from '@/src/ui/SentryQueryInitializer';
import HomeContent from '@/src/ui/HomeContent';


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
