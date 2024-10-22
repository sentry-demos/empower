'use client'

import Loader from 'react-loader-spinner';

export default function ThreeDotLoader() {
  return (
    <div className="loader-container">
      <Loader type="ThreeDots" color="#f6cfb2" height={150} width={150} />
    </div>
  );
}
