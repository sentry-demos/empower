import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import * as Sentry from '@sentry/angular';

/**
 * ThreeDots Component - Displays an animated loading indicator
 * 
 * This component shows three animated dots that move in sequence:
 * - Creates a "loading..." visual effect
 * - Customizable color, height, and width
 * - Smooth CSS animations for professional appearance
 * - Reusable across the application for consistent loading states
 * 
 * Key Features:
 * - Animated dots with staggered timing
 * - Customizable appearance through inputs
 * - Pure CSS animations for performance
 * - Responsive design that scales with parent container
 * 
 * Usage Examples:
 * - Product loading states
 * - Form submission loading
 * - API call waiting indicators
 * - Any place where you need to show "please wait"
 * 
 * TDA Test Compatibility:
 * - Component structure is simple and testable
 * - No complex interactions that could break automated tests
 * - Consistent appearance across different pages
 */
@Component({
  selector: 'app-three-dots',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './three-dots.component.html',
  styleUrls: ['./three-dots.component.css']
})
@Sentry.TraceClass({ name: "ThreeDotsComponent" })
export class ThreeDotsComponent {
  // Color of the dots (defaults to a warm orange)
  @Input() color: string = '#f6cfb2';
  
  // Height of the component in pixels (defaults to 100px)
  @Input() height: number = 100;
  
  // Width of the component in pixels (defaults to 100px)
  @Input() width: number = 100;

  /**
   * Gets the CSS styles for the component container
   * Applies the custom height and width inputs
   * 
   * @returns Object with CSS styles for the component
   */
  getContainerStyles(): { [key: string]: string } {
    return {
      height: `${this.height}px`,
      width: `${this.width}px`
    };
  }

  /**
   * Gets the CSS styles for individual dots
   * Applies the custom color input to each dot
   * 
   * @returns Object with CSS styles for the dots
   */
  getDotStyles(): { [key: string]: string } {
    return {
      backgroundColor: this.color
    };
  }
}
