import ThreeDotLoader from '../../ui/ThreeDotLoader';
import ProductCatalog from '../../ui/ProductCatalog';
import { Suspense } from 'react';

export const dynamic = 'force-dynamic';

export default function Products(props) {
  return (
    <Suspense fallback={<ThreeDotLoader />}>
      <ProductCatalog />
    </Suspense>
  );
}
