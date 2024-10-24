import ThreeDotLoader from '/src/ui/ThreeDotLoader';
import ProductCatalog from '/src/ui/ProductCatalog';
import { Suspense } from 'react';

export const dynamic = 'force-dynamic';

export default function Products() {
  return (
    <Suspense fallback={<ThreeDotLoader />}>
      <ProductCatalog />
    </Suspense>
  );
}
