import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import * as Sentry from '@sentry/angular';

@Component({
  selector: 'app-complete-error',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './complete-error.component.html',
  styleUrls: ['./complete-error.component.css']
})
export class CompleteErrorComponent implements OnInit {

  constructor() {}

  ngOnInit() {
    // Flush replay like React
    window.setTimeout(() => {
      const replay = Sentry.getReplay();
      if (replay) {
        replay.flush();
      }
    }, 1000);
  }

  // Handle feedback button click
  onFeedbackClick() {
    // In a real implementation, this would show a feedback dialog
  }

  // Handle contact us button click (like React)
  onContactUsClick() {
    // In a real implementation, this would open a contact form
  }
}
