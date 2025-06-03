import ThreeDotLoader from '@/src/ui/ThreeDotLoader';
import ProductCatalog from '@/src/ui/products/ProductCatalog';
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
