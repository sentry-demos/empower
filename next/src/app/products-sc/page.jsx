import ThreeDotLoader from '/ui/loader';
import ProductCatalog from '/ui/product-catalog';
import { Suspense } from 'react';

export const dynamic = 'force-dynamic';

export default function Products(props) {
  return (
    <Suspense fallback={<ThreeDotLoader />}>
      <ProductCatalog />
    </Suspense>
  );
}
