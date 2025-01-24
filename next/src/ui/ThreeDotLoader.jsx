'use client'

import { ThreeDots } from 'react-loader-spinner';

export default function ThreeDotLoader() {
  return (
    <div className="loader-container">
      <ThreeDots color="#f6cfb2" height={150} width={150} />
    </div>
  );
}
