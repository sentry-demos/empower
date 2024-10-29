
import React from 'react';
import { getProduct } from '@/lib/data';
import { Suspense } from 'react';
import ThreeDotLoader from '@/src/ui/ThreeDotLoader';
import ProductPage from '@/src/components/ProductPage';
import { notFound } from 'next/navigation';

export default async function Product({ params }) {
  const product = await getProduct((await params).id);
  console.log(product);

  if (!product) {
    notFound();
  }

  return (
    <Suspense fallback={<ThreeDotLoader />}>
      <ProductPage product={product} />
    </Suspense>

  );
}
