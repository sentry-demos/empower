import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, ActivatedRoute, Router } from '@angular/router';

/**
 * Employee interface - defines the structure of employee data
 */
interface Employee {
  name: string;
  bio: string;
  url: string;
  img: string;
}

/**
 * Employee Component - Displays detailed information about a specific employee
 * 
 * This component shows employee details including:
 * - Employee profile image
 * - Name and biography
 * - Navigation back to the about page
 * - Loading state handling
 * 
 * Key Features:
 * - Loads employee data based on route parameters
 * - Handles loading and error states gracefully
 * - Responsive design for different screen sizes
 * - Safe navigation with null checking
 * 
 * TDA Test Compatibility:
 * - Navigation patterns match React app for automated testing
 * - Button styling is consistent across frameworks
 * - Component structure mirrors React implementation
 */
@Component({
  selector: 'app-employee',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './employee.component.html',
  styleUrls: ['./employee.component.css']
})
export class EmployeeComponent implements OnInit {
  // Employee data object - can be null while loading
  employee: Employee | null = null;
  
  // Flag to show loading state
  loading = true;
  
  // Flag to show error state
  error = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    // Get the employee ID from the URL route parameters
    // This allows the component to load different employees based on the URL
    this.route.params.subscribe(params => {
      const employeeId = params['id'];
      
      if (employeeId) {
        // Load employee data when component initializes
        this.loadEmployee(employeeId);
      } else {
        // Handle case where no ID is provided
        this.error = true;
        this.loading = false;
      }
    });
  }

  /**
   * Loads employee data based on the employee ID
   * Uses a predefined map of employees for demo purposes
   * 
   * @param employeeId - The ID of the employee to load
   */
  loadEmployee(employeeId: string): void {
    this.loading = true;
    this.error = false;
    
    // Map of available employees (demo data)
    const employeeMap: { [key: string]: Employee } = {
      'jane': { 
        name: 'Jane Schmidt', 
        bio: 'CEO of Empower Plant. Jane is also an environmentalist. Okay, so she\'s no Greta Thurnberg, but she brings her own mug for take-away coffee and uses public transportation whenever possible.', 
        url: 'jane', 
        img: './assets/jane-schmidt.jpg' 
      },
      'lily': { 
        name: 'Lily Chan', 
        bio: 'CTO of Empower Plant. Lily is a former Google engineer who left the tech giant to pursue her passion for plants and IoT.', 
        url: 'lily', 
        img: './assets/lily-chen.jpg' 
      },
      'keith': { 
        name: 'Keith Ryan', 
        bio: 'Head of Engineering at Empower Plant. Keith has 15 years of experience in IoT and sensor technology.', 
        url: 'keith', 
        img: './assets/keith-johnson.jpg' 
      },
      'mason': { 
        name: 'Mason Kim', 
        bio: 'Lead Designer at Empower Plant. Mason specializes in user experience and plant-friendly interface design.', 
        url: 'mason', 
        img: './assets/mason-williams.jpg' 
      },
      'emma': { 
        name: 'Emma Garcia', 
        bio: 'Marketing Director at Empower Plant. Emma leads our plant advocacy and community engagement efforts.', 
        url: 'emma', 
        img: './assets/emma-davis.jpg' 
      },
      'noah': { 
        name: 'Noah Miller', 
        bio: 'Plant Scientist at Empower Plant. Noah has a PhD in botany and leads our plant research initiatives.', 
        url: 'noah', 
        img: './assets/noah-rodriguez.jpg' 
      }
    };

    // Get employee data from the map
    const employee = employeeMap[employeeId];
    
    if (employee) {
      // Successfully found employee data
      this.employee = employee;
      this.loading = false;
    } else {
      // Employee not found
      this.error = true;
      this.loading = false;
      console.error('Employee not found with ID:', employeeId);
    }
  }
}
