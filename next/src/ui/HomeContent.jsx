'use client'

import Footer from "@/src/ui/Footer";
import { Provider } from 'react-redux';
import { store } from '@/src/utils/store';
import ScrollToTop from '@/src/ui/ScrollToTop';
import Nav from '@/src/ui/Nav';

import '@/src/styles/index.css';
import '@/src/styles/footer.css';
import '@/src/styles/nav.css';
import '@/src/styles/products.css';
import '@/src/styles/about.css';
import '@/src/styles/cart.css';
import '@/src/styles/checkout.css';
import '@/src/styles/complete.css';
import '@/src/styles/product.css';



export default function HomeContent({ children }) {


  
  return (
    <>
      <Provider store={store}>
        <ScrollToTop />
        <Nav />
        <div id="body-container">
          {children}
        </div>
      </Provider>
      <Footer />
    </>
  )
}
