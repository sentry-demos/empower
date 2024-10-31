import ThreeDotLoader from '/src/components/ThreeDotLoader';
import ProductCatalog from '/src/components/ProductCatalog';
import { Suspense } from 'react';

export const dynamic = 'force-dynamic';
export const fetchCache = 'force-no-store';


export default function Products() {
  return (
    <Suspense fallback={<ThreeDotLoader />}>
      <ProductCatalog />
    </Suspense>
  );
}
