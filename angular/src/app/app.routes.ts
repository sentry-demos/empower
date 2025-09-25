import { Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { ProductsComponent } from './components/products/products.component';
import { ProductDetailComponent } from './components/product-detail/product-detail.component';
import { AboutComponent } from './components/about/about.component';
import { EmployeeComponent } from './components/employee/employee.component';
import { CartComponent } from './components/cart/cart.component';
import { CheckoutComponent } from './components/checkout/checkout.component';
import { CompleteComponent } from './components/complete/complete.component';
import { CompleteErrorComponent } from './components/complete-error/complete-error.component';

export const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'home', component: HomeComponent },
  { path: 'about', component: AboutComponent },
  { path: 'products', component: ProductsComponent },
  { path: 'products-fes', component: ProductsComponent }, // Frontend slowdown route like React
  { path: 'product/:id', component: ProductDetailComponent }, // Product detail route like React
  { path: 'employee/:id', component: EmployeeComponent }, // Employee detail route like React
  { path: 'cart', component: CartComponent }, // Cart route like React
  { path: 'checkout', component: CheckoutComponent }, // Checkout route like React
  { path: 'complete', component: CompleteComponent }, // Success page like React
  { path: 'error', component: CompleteErrorComponent }, // Error page like React
  { path: '**', redirectTo: '/' }
];
