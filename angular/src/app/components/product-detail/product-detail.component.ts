import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, ActivatedRoute, Router } from '@angular/router';
import { ProductsService, Product } from '../../services/products.service';
import { CartService } from '../../services/cart.service';

@Component({
  selector: 'app-product-detail',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './product-detail.component.html',
  styleUrls: ['./product-detail.component.css']
})
export class ProductDetailComponent implements OnInit {
  product: Product | null = null;
  averageRating: string = '0.0';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private productsService: ProductsService,
    private cartService: CartService
  ) {}

  ngOnInit() {
    // Get product data from router state (like React's location.state)
    const navigation = this.router.getCurrentNavigation();
    if (navigation?.extras.state) {
      // Product data passed via router state (instant loading like React)
      this.product = navigation.extras.state as Product;
      this.calculateAverageRating();
    } else {
      // Fallback: get product ID from route parameters and load from API
      this.route.params.subscribe(params => {
        const productId = +params['id'];
        
        // Load product data from the service
        this.loadProduct(productId);
      });
    }
  }

  private loadProduct(productId: number) {
    // Fallback method - only used if no router state
    this.productsService.getProducts().subscribe({
      next: (products) => {
        this.product = products.find(p => p.id === productId) || null;
        if (this.product) {
          this.calculateAverageRating();
        } else {
          console.error('Product not found with ID:', productId);
        }
      },
      error: (error) => {
        console.error('Error loading product:', error);
      }
    });
  }

  private calculateAverageRating() {
    if (this.product && this.product.reviews && this.product.reviews.length > 0) {
      const totalRating = this.product.reviews.reduce((sum, review) => sum + review.rating, 0);
      this.averageRating = (totalRating / this.product.reviews.length).toFixed(1);
    }
  }

  addToCart(product: Product) {
    // Simple inventory validation like React
    const inventory = [3, 4, 5, 6];
    if (inventory.includes(product.id)) {
      // Add to cart using the cart service
      this.cartService.addProduct(product);
    } else {
    }
  }
}
