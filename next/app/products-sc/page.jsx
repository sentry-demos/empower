
import ThreeDotLoader from '/ui/loader';
import ProductCatalog from '/ui/product-catalog';
import { Suspense } from 'react';


export default function Products(props) {
  console.log(props);
  return (
    <Suspense fallback={<ThreeDotLoader />}>
      <ProductCatalog />
    </Suspense>
  )
}