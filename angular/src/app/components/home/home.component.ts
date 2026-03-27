import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

/**
 * Home Component - Displays the main landing page
 * 
 * This component shows the hero section with:
 * - Background image of plants
 * - Welcome message and tagline
 * - Call-to-action button to browse products
 * - Support for frontend slowdown demo mode
 * 
 * Key Features:
 * - Dynamic background image loading
 * - Responsive hero layout
 * - Navigation to products page
 * - Demo mode support for testing
 * 
 * TDA Test Compatibility:
 * - Button styling matches React app for automated testing
 * - Navigation patterns are consistent across frameworks
 * - Hero section structure mirrors React implementation
 */
@Component({
  selector: 'app-home',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent {
  // Background image for the hero section
  backgroundImage = './assets/plants-background-img.jpg';
  
  // Flag to enable frontend slowdown demo mode
  // This simulates slow rendering for performance testing
  frontendSlowdown = false;

  constructor() {
    
    // Check URL for frontend slowdown parameter
    // This allows demo users to test performance monitoring
    const urlParams = new URLSearchParams(window.location.search);
    const currentPath = window.location.pathname;
    
    // Enable slowdown mode if URL contains specific path or parameter
    this.frontendSlowdown = currentPath === '/products-fes' || urlParams.get('frontendSlowdown') === 'true';
  }
}
