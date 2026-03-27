import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { employees } from '../../data/employees';
import { slugify } from '../../utils/slugify';
import { ConfigService } from '../../services/config.service';

@Component({
  selector: 'app-about',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './about.component.html',
  styleUrls: ['./about.component.css']
})
export class AboutComponent implements OnInit {
  employees = employees;

  constructor(private router: Router, private configService: ConfigService) {}

  ngOnInit() {
    // Mirror React's additional API calls for performance optimization
    this.makeAdditionalApiCalls();
    
    // Mirror React's busy_sleep logic (simplified version)
    if (!this.isOddReleaseWeek()) {
      this.busySleep(Math.random() * 25 + 100);
    }
  }

  /**
   * Makes additional API calls to test backend connectivity
   * These are expected to fail and demonstrate error handling
   */
  private async makeAdditionalApiCalls() {
    // Use config service for backend URL (supports Laravel/Flask switching)
    const backendUrl = this.configService.getBackendUrl();
    const backendType = this.configService.getCurrentBackendType();
    
    
    const endpoints = ['/api', '/organization', '/connect'];
    
    for (const endpoint of endpoints) {
      try {
        const response = await fetch(backendUrl + endpoint, {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' }
        });
        
        if (!response.ok) {
        }
      } catch (err) {
      }
    }
  }

  // Mirror React's isOddReleaseWeek logic (simplified)
  private isOddReleaseWeek(): boolean {
    const now = new Date();
    const weekNumber = Math.ceil((now.getTime() - new Date(now.getFullYear(), 0, 1).getTime()) / (7 * 24 * 60 * 60 * 1000));
    return weekNumber % 2 === 1;
  }

  // Mirror React's busy_sleep logic (simplified)
  private busySleep(ms: number) {
    const start = Date.now();
    while (Date.now() - start < ms) {
      // Busy wait
    }
  }

  // Navigate to employee detail page
  onEmployeeClick(employee: any) {
    const slug = slugify(employee.url);
    this.router.navigate(['/employee', slug], { state: employee });
  }

  // TrackBy function for ngFor optimization
  trackByEmployee(index: number, employee: any): string {
    return employee.name;
  }
}
